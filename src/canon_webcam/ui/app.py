"""Composition root: aplicação Tkinter que liga domínio, serviços e UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

import cv2
from PIL import Image, ImageTk

from canon_webcam.capture.edsdk_source import EdsdkSource
from canon_webcam.capture.factory import create_source
from canon_webcam.domain.devices import BackendKind
from canon_webcam.domain.settings import EXPOSURE_SETTINGS
from canon_webcam.output.virtual_cam import VirtualWebcam
from canon_webcam.processing.hud_remover import HUDRemover
from canon_webcam.services.camera_control import CameraControl
from canon_webcam.services.pipeline import PreviewPipeline
from canon_webcam.services.scanner import CameraScanner
from canon_webcam.ui.panels import CameraControlPanel, ConnectionPanel, HudSettingsPanel, InfoPanel, OutputPanel

BG_COLOR = "#1a1a2e"
MIN_WIDTH, MIN_HEIGHT = 850, 620


class CanonWebcamApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canon T5i - Webcam")
        self.root.geometry("1050x720")
        self.root.minsize(MIN_WIDTH, MIN_HEIGHT)
        self.root.configure(bg=BG_COLOR)

        self._processor = HUDRemover()
        self._scanner = CameraScanner()
        self._pipeline: PreviewPipeline | None = None
        self._camera_control: CameraControl | None = None
        self._virtual_cam = VirtualWebcam(width=1280, height=720, fps=30)

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._scan_devices()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background=BG_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00d4ff")
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#888888")
        style.configure("Mode.TLabel", font=("Segoe UI", 9, "bold"), foreground="#f39c12")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        header = ttk.Frame(main_frame)
        header.grid(row=0, column=0, sticky=tk.EW, pady=(0, 10))
        ttk.Label(header, text="Canon T5i - Virtual Webcam", style="Header.TLabel").pack(side=tk.LEFT)

        content = ttk.Frame(main_frame)
        content.grid(row=1, column=0, sticky=tk.NSEW)

        preview_frame = tk.Frame(content, bg="#000000", bd=2, relief=tk.SUNKEN)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._preview_label = tk.Label(preview_frame, bg="#000000", text="Preview",
                                       fg="#666666", font=("Segoe UI", 16))
        self._preview_label.pack(fill=tk.BOTH, expand=True)

        right_panel = ttk.Frame(content, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self._connection = ConnectionPanel(
            right_panel, self._scan_devices, self._connect_camera, self._disconnect_camera
        )
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._hud_panel = HudSettingsPanel(
            right_panel, self._on_hud_changed, self._apply_crop, self._auto_detect_hud
        )
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._camera_ctrl = CameraControlPanel(
            right_panel, self._set_camera_value, self._auto_focus, self._focus_near, self._focus_far
        )
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._output_panel = OutputPanel(right_panel, self._start_virtual_cam, self._stop_virtual_cam)
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._info_panel = InfoPanel(right_panel)

        header_label = ttk.Label(header, textvariable=self._connection.status_var, style="Status.TLabel")
        header_label.pack(side=tk.RIGHT)

    # ------------------------------------------------------------------
    # Scan / conexão
    # ------------------------------------------------------------------
    def _scan_devices(self) -> None:
        self._scanner = CameraScanner(include_edsdk=self._connection.use_edsdk)
        devices = self._scanner.scan()
        self._connection.set_devices(devices)

    def _connect_camera(self) -> None:
        device = self._connection.selected_device()
        if device is None:
            messagebox.showwarning("No Device", "Select a device first, or click Scan Devices.")
            return

        try:
            self._pipeline = PreviewPipeline(create_source(device), self._processor)
            if not self._pipeline.start():
                raise RuntimeError(f"Cannot open video device {device.name}")

            self._on_connected(device)
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self._connection.set_status("Connection failed")

    def _on_connected(self, device) -> None:
        self._connection.set_connected(True)

        source = self._pipeline.source
        if device.backend == BackendKind.EDSDK and isinstance(source, EdsdkSource):
            self._camera_control = CameraControl(source.sdk)
            self._connection.set_status(f"Connected: {device.name}")
            self._connection.set_mode("Mode: Canon EDSDK (Live View)")
            self._camera_ctrl.set_enabled(True)
            self._refresh_camera_values()
        else:
            self._camera_control = None
            self._connection.set_status(f"Connected: {device.name}")
            self._connection.set_mode("Mode: DirectShow (EOS Webcam Utility)")

        self._wire_pipeline()
        self._pipeline.set_frame_handler(self._on_frame)

    def _wire_pipeline(self) -> None:
        if self._pipeline is not None:
            self._pipeline.add_output(self._virtual_cam)

    def _disconnect_camera(self) -> None:
        if self._pipeline is not None:
            self._pipeline.stop()
            self._pipeline = None
        self._stop_virtual_cam(silent=True)

        self._camera_control = None
        self._camera_ctrl.set_enabled(False)
        self._camera_ctrl.set_status("")

        self._connection.set_connected(False)
        self._connection.set_status("Disconnected")
        self._connection.set_mode("")
        self._clear_preview()

    # ------------------------------------------------------------------
    # Preview / frame handler
    # ------------------------------------------------------------------
    def _on_frame(self, frame, fps: float) -> None:
        self._update_preview(frame)
        self._info_panel.set_fps(fps)

    def _update_preview(self, frame) -> None:
        try:
            preview_w = self._preview_label.winfo_width()
            preview_h = self._preview_label.winfo_height()

            if preview_w <= 1 or preview_h <= 1:
                preview_w, preview_h = 640, 480

            display = cv2.resize(frame, (preview_w, preview_h))
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(display)
            imgtk = ImageTk.PhotoImage(image=img)

            self._preview_label.configure(image=imgtk, text="")
            self._preview_label._imgtk = imgtk
        except Exception:
            pass

    def _clear_preview(self) -> None:
        if self._preview_label:
            self._preview_label.configure(image="", text="Preview")
            self._preview_label._imgtk = None

    # ------------------------------------------------------------------
    # HUD
    # ------------------------------------------------------------------
    def _on_hud_changed(self) -> None:
        self._hud_panel.apply_to_processor(self._processor)

    def _apply_crop(self) -> None:
        self._hud_panel.apply_crop_to_processor(self._processor)

    def _auto_detect_hud(self) -> None:
        frame = self._pipeline.current_frame() if self._pipeline else None
        if frame is None:
            return
        regions = self._processor.detect_hud_text_regions(frame)
        self._processor.clear_hud_regions()
        for region in regions:
            self._processor.add_hud_region(*region)
        self._processor.set_blur_hud(True)
        self._hud_panel.set_blur(True)
        messagebox.showinfo("Auto Detect", f"Detected {len(regions)} HUD regions")

    # ------------------------------------------------------------------
    # Controle de câmera
    # ------------------------------------------------------------------
    def _refresh_camera_values(self) -> None:
        if self._camera_control is None:
            return
        for key, setting in EXPOSURE_SETTINGS.items():
            self._camera_ctrl.populate(
                key, setting.table.labels, self._camera_control.current_label(key)
            )

    def _set_camera_value(self, key: str, label: str) -> None:
        if self._camera_control is None:
            return
        result = self._camera_control.set_by_label(key, label)
        if result != 0:
            self._camera_ctrl.set_status(f"Set {key} -> 0x{result:08X}")
        else:
            self._camera_ctrl.set_status(f"{key}: {label} applied")
            self._refresh_camera_values()

    def _auto_focus(self) -> None:
        if self._camera_control is None:
            return
        result = self._camera_control.focus_auto()
        self._camera_ctrl.set_status("Auto Focus -> 0x%08X" % result)

    def _focus_near(self) -> None:
        if self._camera_control is None:
            return
        result = self._camera_control.focus_near()
        self._camera_ctrl.set_status(f"Focus drive (Near) -> 0x{result:08X}")

    def _focus_far(self) -> None:
        if self._camera_control is None:
            return
        result = self._camera_control.focus_far()
        self._camera_ctrl.set_status(f"Focus drive (Far) -> 0x{result:08X}")

    # ------------------------------------------------------------------
    # Virtual cam
    # ------------------------------------------------------------------
    def _start_virtual_cam(self) -> None:
        width, height = self._output_panel.resolution
        fps = self._output_panel.fps

        self._processor.set_target_resolution(width, height)
        self._virtual_cam = VirtualWebcam(width=width, height=height, fps=fps)

        if self._virtual_cam.start():
            self._output_panel.set_running(True)
            self._wire_pipeline()
            self._connection.set_status(f"Virtual Cam ON ({self._virtual_cam.backend_name})")
        else:
            messagebox.showerror(
                "Virtual Cam Error",
                "Failed to start virtual camera.\n\n"
                "Install OBS Studio (free) - it includes a virtual camera.\n"
                "https://obsproject.com",
            )

    def _stop_virtual_cam(self, silent: bool = False) -> None:
        self._virtual_cam.stop()
        self._output_panel.set_running(False)
        if not silent:
            self._connection.set_status("Disconnected" if self._pipeline is None else "Connected")

    # ------------------------------------------------------------------
    # Fechamento
    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        if self._pipeline is not None:
            self._pipeline.stop()
            self._pipeline = None
        try:
            self._virtual_cam.stop()
        except Exception:
            pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()