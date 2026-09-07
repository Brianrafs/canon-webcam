import sys
import os
import time
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk

from processor import HUDRemover
from virtual_cam import VirtualWebcam
from edsdk import ISO_TABLE, AV_TABLE, TV_TABLE


def list_directshow_devices():
    devices = []
    found_indexes = []

    for i in range(4):
        for backend in (cv2.CAP_MSMF, cv2.CAP_DSHOW):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    backend_name = "MSMF" if backend == cv2.CAP_MSMF else "DSHOW"
                    name = "Canon T5i (EOS Webcam Utility)" if i == 0 else f"Device {i}"
                    devices.append({
                        "index": i,
                        "backend": backend,
                        "name": name,
                        "resolution": f"{w}x{h}",
                        "label": f"{name} ({backend_name}) {w}x{h}"
                    })
                    found_indexes.append(i)
                    cap.release()
                    break
            except Exception:
                continue

    return devices


def try_edsdk_connection():
    try:
        from edsdk import CanonEDSDK
        sdk = CanonEDSDK()
        sdk.initialize()

        for attempt in range(5):
            cameras = sdk.get_camera_list()
            if cameras:
                return sdk, cameras
            print(f"[EDSDK] scan attempt {attempt + 1}: no cameras yet, retrying...")
            time.sleep(1.0)

        sdk.terminate()
    except Exception as e:
        print(f"[Fallback] EDSDK not available: {e}")
    return None, []


class CanonWebcamApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Canon T5i - Webcam")
        self.root.geometry("1050x720")
        self.root.minsize(850, 620)
        self.root.configure(bg="#1a1a2e")

        self.hud_remover = HUDRemover()
        self.virtual_cam = VirtualWebcam(width=1280, height=720, fps=30)

        self._running = False
        self._preview_running = False
        self._camera_connected = False
        self._capture_mode = None
        self._edsdk = None
        self._opencv_cap = None
        self._preview_thread = None
        self._frame = None
        self._frame_lock = threading.Lock()

        self._preview_label = None
        self._status_var = tk.StringVar(value="Disconnected")
        self._battery_var = tk.StringVar(value="Battery: --")
        self._fps_var = tk.StringVar(value="FPS: 0")
        self._resolution_var = tk.StringVar(value="--")
        self._hud_blur_var = tk.BooleanVar(value=True)
        self._auto_crop_var = tk.BooleanVar(value=False)
        self._use_edsdk_var = tk.BooleanVar(value=False)
        self._crop_x_var = tk.IntVar(value=0)
        self._crop_y_var = tk.IntVar(value=0)
        self._crop_w_var = tk.IntVar(value=0)
        self._crop_h_var = tk.IntVar(value=0)

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._scan_devices()

    def _build_ui(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#00d4ff")
        style.configure("Status.TLabel", font=("Segoe UI", 9), foreground="#888888")
        style.configure("Mode.TLabel", font=("Segoe UI", 9, "bold"), foreground="#f39c12")

        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Canon T5i - Virtual Webcam", style="Header.TLabel").pack(side=tk.LEFT)
        self._status_label = ttk.Label(header, textvariable=self._status_var, style="Status.TLabel")
        self._status_label.pack(side=tk.RIGHT)

        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        preview_frame = tk.Frame(content, bg="#000000", bd=2, relief=tk.SUNKEN)
        preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self._preview_label = tk.Label(preview_frame, bg="#000000", text="Preview", fg="#666666", font=("Segoe UI", 16))
        self._preview_label.pack(fill=tk.BOTH, expand=True)

        right_panel = ttk.Frame(content, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        self._build_connection_section(right_panel)
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._build_hud_section(right_panel)
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._build_camera_controls_section(right_panel)
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._build_virtual_cam_section(right_panel)
        ttk.Separator(right_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)
        self._build_info_section(right_panel)

    def _build_connection_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Camera Source", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        self._mode_label = ttk.Label(frame, text="", style="Mode.TLabel")
        self._mode_label.pack(anchor=tk.W)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self._scan_btn = ttk.Button(btn_frame, text="Scan Devices", command=self._scan_devices)
        self._scan_btn.pack(side=tk.LEFT, padx=(0, 5))

        self._connect_btn = ttk.Button(btn_frame, text="Start", command=self._connect_camera)
        self._connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        self._disconnect_btn = ttk.Button(btn_frame, text="Stop", command=self._disconnect_camera, state=tk.DISABLED)
        self._disconnect_btn.pack(side=tk.LEFT)

        ttk.Checkbutton(
            frame, text="Scan via EDSDK (advanced)",
            variable=self._use_edsdk_var
        ).pack(anchor=tk.W, pady=(4, 0))

        self._device_combo = ttk.Combobox(frame, state="readonly", width=35)
        self._device_combo.pack(fill=tk.X, pady=2)

    def _build_hud_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="HUD Control", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        ttk.Checkbutton(
            frame, text="Blur HUD areas",
            variable=self._hud_blur_var,
            command=self._on_hud_setting_changed
        ).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(
            frame, text="Custom crop",
            variable=self._auto_crop_var,
            command=self._on_hud_setting_changed
        ).pack(anchor=tk.W, pady=2)

        crop_frame = ttk.Frame(frame)
        crop_frame.pack(fill=tk.X, pady=2)

        ttk.Label(crop_frame, text="X:").grid(row=0, column=0)
        ttk.Spinbox(crop_frame, from_=0, to=1920, width=5, textvariable=self._crop_x_var).grid(row=0, column=1, padx=2)
        ttk.Label(crop_frame, text="Y:").grid(row=0, column=2)
        ttk.Spinbox(crop_frame, from_=0, to=1080, width=5, textvariable=self._crop_y_var).grid(row=0, column=3, padx=2)

        ttk.Label(crop_frame, text="W:").grid(row=1, column=0)
        ttk.Spinbox(crop_frame, from_=0, to=1920, width=5, textvariable=self._crop_w_var).grid(row=1, column=1, padx=2)
        ttk.Label(crop_frame, text="H:").grid(row=1, column=2)
        ttk.Spinbox(crop_frame, from_=0, to=1080, width=5, textvariable=self._crop_h_var).grid(row=1, column=3, padx=2)

        ttk.Button(frame, text="Apply Crop", command=self._apply_crop).pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="Auto Detect HUD", command=self._auto_detect_hud).pack(fill=tk.X, pady=2)

    def _build_camera_controls_section(self, parent):
        from edsdk import (
            kEds_PropertyID_ISOSpeed, kEds_PropertyID_Av, kEds_PropertyID_Tv,
        )
        self._camera_ctrl_pids = {
            "iso": (kEds_PropertyID_ISOSpeed, ISO_TABLE),
            "av": (kEds_PropertyID_Av, AV_TABLE),
            "tv": (kEds_PropertyID_Tv, TV_TABLE),
        }

        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Camera Controls", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        self._cam_ctrl_hint = ttk.Label(
            frame, text="Requires EDSDK connection\n(DirectShow mode cannot control the camera)",
            style="Status.TLabel", wraplength=280
        )
        self._cam_ctrl_hint.pack(anchor=tk.W, pady=(0, 4))

        self._ctrl_combo_objs = {}
        for key, label in (("iso", "ISO"), ("av", "Aperture (Av)"), ("tv", "Shutter (Tv)")):
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=label, width=12).pack(side=tk.LEFT)
            combo = ttk.Combobox(row, state="readonly", width=11)
            combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Button(row, text="Set", width=4,
                       command=lambda k=key: self._set_camera_value(k)).pack(side=tk.LEFT, padx=(4, 0))
            self._ctrl_combo_objs[key] = combo

        self._ctrl_value_maps = {}
        self._refresh_camera_values()

        focus_row = ttk.Frame(frame)
        focus_row.pack(fill=tk.X, pady=(5, 2))
        ttk.Button(focus_row, text="Auto Focus", command=self._auto_focus).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(focus_row, text="Near", command=lambda: self._drive_lens(0x00000001)).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2))
        ttk.Button(focus_row, text="Far", command=lambda: self._drive_lens(0x00008001)).pack(side=tk.LEFT, expand=True, fill=tk.X)

        self._cam_ctrl_status = tk.StringVar(value="")
        ttk.Label(frame, textvariable=self._cam_ctrl_status, style="Status.TLabel").pack(anchor=tk.W)

        self._set_camera_controls_enabled(False)

    def _refresh_camera_values(self):
        for key, (pid, table) in self._camera_ctrl_pids.items():
            combo = self._ctrl_combo_objs.get(key)
            if combo is None:
                continue
            labels = list(table.values())
            self._ctrl_value_maps[key] = dict(table)  # label -> code
            combo["values"] = labels
            current = None
            if self._edsdk and self._camera_connected:
                raw = self._edsdk.get_property_u32(pid)
                if raw is not None:
                    current = table.get(raw)
            if current is None:
                current = labels[0]
            combo.set(current)

    def _set_camera_controls_enabled(self, enabled):
        if not enabled and getattr(self, "_ctrl_combo_objs", None):
            for combo in self._ctrl_combo_objs.values():
                combo.config(state="readonly" if enabled else "disabled")

    def _set_camera_value(self, key):
        if not (self._edsdk and self._camera_connected):
            return
        pid, table = self._camera_ctrl_pids[key]
        combo = self._ctrl_combo_objs.get(key)
        label = combo.get()
        code = next((c for c, l in table.items() if l == label), None)
        if code is None:
            self._cam_ctrl_status.set(f"{key}: invalid value")
            return
        r = self._edsdk.set_property_u32(pid, code)
        if r != 0:
            self._cam_ctrl_status.set(f"Set {key} -> 0x{r:08X}")
        else:
            self._cam_ctrl_status.set(f"{key}: {label} applied")
            self._refresh_camera_values()

    def _auto_focus(self):
        if not (self._edsdk and self._camera_connected):
            return
        r = self._edsdk.auto_focus()
        self._cam_ctrl_status.set("Auto Focus -> 0x%08X" % r)

    def _drive_lens(self, direction):
        if not (self._edsdk and self._camera_connected):
            return
        r = self._edsdk.drive_lens(direction)
        self._cam_ctrl_status.set("Focus drive -> 0x%08X" % r)

    def _build_virtual_cam_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Virtual Webcam Output", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        res_frame = ttk.Frame(frame)
        res_frame.pack(fill=tk.X, pady=2)
        ttk.Label(res_frame, text="Resolution:").pack(side=tk.LEFT)
        self._res_combo = ttk.Combobox(res_frame, values=["640x480", "1280x720", "1920x1080"], width=12, state="readonly")
        self._res_combo.set("1280x720")
        self._res_combo.pack(side=tk.RIGHT)

        fps_frame = ttk.Frame(frame)
        fps_frame.pack(fill=tk.X, pady=2)
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        self._fps_combo = ttk.Combobox(fps_frame, values=["24", "25", "30", "60"], width=12, state="readonly")
        self._fps_combo.set("30")
        self._fps_combo.pack(side=tk.RIGHT)

        self._start_vcam_btn = ttk.Button(frame, text="Start Virtual Cam", command=self._start_virtual_cam)
        self._start_vcam_btn.pack(fill=tk.X, pady=(5, 2))

        self._stop_vcam_btn = ttk.Button(frame, text="Stop Virtual Cam", command=self._stop_virtual_cam, state=tk.DISABLED)
        self._stop_vcam_btn.pack(fill=tk.X)

    def _build_info_section(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Info", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._battery_var, style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._fps_var, style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._resolution_var, style="Status.TLabel").pack(anchor=tk.W)

    def _scan_devices(self):
        self._device_list = []
        values = []

        if self._use_edsdk_var.get():
            sdk, cameras = try_edsdk_connection()
            if cameras:
                for c in cameras:
                    idx = len(self._device_list)
                    self._device_list.append({"type": "edsdk", "sdk": sdk, "camera": c, "index": idx})
                    values.append(f"[SDK] {c['name']} ({c['body_id']})")

        dshow_devices = list_directshow_devices()
        for dev in dshow_devices:
            idx = len(self._device_list)
            self._device_list.append({"type": "dshow", "index": dev["index"], "backend": dev.get("backend")})
            values.append(f"[Video] {dev['label']}")

        self._device_combo["values"] = values
        if values:
            self._device_combo.current(0)
        self._mode_label.configure(text=f"Found {len(self._device_list)} device(s)")

    def _connect_camera(self):
        sel = self._device_combo.current()
        if sel < 0 or sel >= len(self._device_list):
            messagebox.showwarning("No Device", "Select a device first, or click Scan Devices.")
            return

        device = self._device_list[sel]

        try:
            if device["type"] == "edsdk":
                self._connect_edsdk(device)
            elif device["type"] == "dshow":
                self._connect_dshow(device)
            else:
                messagebox.showwarning("No Device", "No valid device selected.")
                return

            self._camera_connected = True
            self._connect_btn.config(state=tk.DISABLED)
            self._disconnect_btn.config(state=tk.NORMAL)
            self._scan_btn.config(state=tk.DISABLED)
            self._start_preview()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self._status_var.set("Connection failed")

    def _connect_edsdk(self, device):
        self._status_var.set("Connecting via EDSDK...")
        self.root.update()

        from edsdk import CanonEDSDK
        self._edsdk = CanonEDSDK()
        self._edsdk.initialize()

        name = None
        for attempt in range(5):
            try:
                name = self._edsdk.connect(device["camera"]["index"])
                break
            except Exception as e:
                print(f"[Connect] attempt {attempt + 1} failed: {e}")
                time.sleep(1.0)

        if name is None:
            raise Exception("Failed to connect to camera. Check the camera is on, in Movie mode, not showing a menu.")

        self._capture_mode = "edsdk"
        self._status_var.set(f"Connected: {name}")
        self._mode_label.configure(text="Mode: Canon EDSDK (Live View)")
        self._set_camera_controls_enabled(True)
        self._refresh_camera_values()
        self._cam_ctrl_started = getattr(self, "_cam_ctrl_started", time.time())

    def _connect_dshow(self, device):
        self._status_var.set("Opening video device...")
        self.root.update()

        backends = [device.get("backend")]
        if backends[0] is None:
            backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]
        backends = [b for b in backends if b is not None]

        opened = False
        for backend in backends:
            try:
                if backend == cv2.CAP_ANY:
                    cap = cv2.VideoCapture(device["index"])
                else:
                    cap = cv2.VideoCapture(device["index"], backend)
                if cap.isOpened():
                    self._opencv_cap = cap
                    opened = True
                    break
                cap.release()
            except Exception:
                continue

        if not opened:
            raise Exception(f"Cannot open video device {device['index']}")

        self._opencv_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self._opencv_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        w = int(self._opencv_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(self._opencv_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self._resolution_var.set(f"Input: {w}x{h}")

        self._capture_mode = "dshow"
        self._status_var.set(f"Connected: DirectShow Device {device['index']}")
        self._mode_label.configure(text="Mode: DirectShow (EOS Webcam Utility)")

    def _disconnect_camera(self):
        self._stop_preview()
        self._stop_virtual_cam()

        if self._edsdk:
            try:
                self._edsdk.disconnect()
                self._edsdk.terminate()
            except Exception:
                pass
            self._edsdk = None

        if self._opencv_cap:
            try:
                self._opencv_cap.release()
            except Exception:
                pass
            self._opencv_cap = None

        self._camera_connected = False
        self._capture_mode = None
        self._status_var.set("Disconnected")
        self._mode_label.configure(text="")
        self._set_camera_controls_enabled(False)
        self._connect_btn.config(state=tk.NORMAL)
        self._disconnect_btn.config(state=tk.DISABLED)
        self._scan_btn.config(state=tk.NORMAL)
        self._clear_preview()

    def _start_preview(self):
        if self._preview_running:
            return
        self._preview_running = True
        self._preview_thread = threading.Thread(target=self._preview_loop, daemon=True)
        self._preview_thread.start()

    def _stop_preview(self):
        self._preview_running = False
        if self._preview_thread:
            self._preview_thread.join(timeout=3.0)
            self._preview_thread = None
        if self._edsdk:
            try:
                self._edsdk.stop_live_view()
            except Exception:
                pass

    def _preview_loop(self):
        frame_count = 0
        start_time = time.time()
        live_view_started = False

        while self._preview_running and self._camera_connected:
            frame = None

            if self._capture_mode == "edsdk" and self._edsdk:
                if not live_view_started:
                    try:
                        self._edsdk.start_live_view()
                        live_view_started = True
                        print("[Preview] Live View started")
                    except Exception as e:
                        print(f"[Preview] Live View not started: {e}")
                        time.sleep(1.0)
                        continue
                try:
                    frame = self._edsdk.capture_live_view_frame()
                except Exception:
                    pass
            elif self._capture_mode == "dshow" and self._opencv_cap:
                try:
                    ret, frame = self._opencv_cap.read()
                    if not ret:
                        frame = None
                except Exception:
                    pass

            if frame is not None:
                processed = self.hud_remover.process_frame(frame)

                with self._frame_lock:
                    self._frame = processed.copy()

                if self.virtual_cam.is_active:
                    self.virtual_cam.send_frame(processed)

                self._update_preview(processed)

                frame_count += 1
                elapsed = time.time() - start_time
                if elapsed >= 1.0:
                    fps = frame_count / elapsed
                    self._fps_var.set(f"FPS: {fps:.1f}")
                    frame_count = 0
                    start_time = time.time()
            else:
                time.sleep(0.03)

    def _update_preview(self, frame):
        try:
            preview_w = self._preview_label.winfo_width()
            preview_h = self._preview_label.winfo_height()

            if preview_w <= 1 or preview_h <= 1:
                preview_w = 640
                preview_h = 480

            display = cv2.resize(frame, (preview_w, preview_h))
            display = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(display)
            imgtk = ImageTk.PhotoImage(image=img)

            self._preview_label.configure(image=imgtk, text="")
            self._preview_label._imgtk = imgtk
        except Exception:
            pass

    def _clear_preview(self):
        if self._preview_label:
            self._preview_label.configure(image="", text="Preview")
            self._preview_label._imgtk = None

    def _start_virtual_cam(self):
        res = self._res_combo.get().split("x")
        w, h = int(res[0]), int(res[1])
        fps = int(self._fps_combo.get())

        self.hud_remover.set_target_resolution(w, h)
        self.virtual_cam = VirtualWebcam(width=w, height=h, fps=fps)

        if self.virtual_cam.start():
            self._start_vcam_btn.config(state=tk.DISABLED)
            self._stop_vcam_btn.config(state=tk.NORMAL)
            self._status_var.set(f"Virtual Cam ON ({self.virtual_cam.backend_name})")
        else:
            messagebox.showerror(
                "Virtual Cam Error",
                "Failed to start virtual camera.\n\n"
                "Install OBS Studio (free) - it includes a virtual camera.\n"
                "https://obsproject.com"
            )

    def _stop_virtual_cam(self):
        self.virtual_cam.stop()
        self._start_vcam_btn.config(state=tk.NORMAL)
        self._stop_vcam_btn.config(state=tk.DISABLED)
        if self._camera_connected:
            mode = "EDSDK" if self._capture_mode == "edsdk" else "DirectShow"
            self._status_var.set(f"Connected ({mode})")
        else:
            self._status_var.set("Disconnected")

    def _on_hud_setting_changed(self):
        self.hud_remover.set_blur_hud(self._hud_blur_var.get())
        self.hud_remover.set_auto_crop_enabled(self._auto_crop_var.get())

    def _apply_crop(self):
        x = self._crop_x_var.get()
        y = self._crop_y_var.get()
        w = self._crop_w_var.get()
        h = self._crop_h_var.get()

        if w > 0 and h > 0:
            self.hud_remover.set_crop_region(x, y, w, h)
            self.hud_remover.set_auto_crop_enabled(True)
            self._auto_crop_var.set(True)
            self._on_hud_setting_changed()

    def _auto_detect_hud(self):
        with self._frame_lock:
            if self._frame is not None:
                regions = self.hud_remover.detect_hud_text_regions(self._frame)
                self.hud_remover.clear_hud_regions()
                for r in regions:
                    self.hud_remover.add_hud_region(*r)
                self.hud_remover.set_blur_hud(True)
                self._hud_blur_var.set(True)
                messagebox.showinfo("Auto Detect", f"Detected {len(regions)} HUD regions")

    def _on_close(self):
        self._preview_running = False
        self._running = False

        try:
            self.virtual_cam.stop()
        except Exception:
            pass

        if self._edsdk:
            try:
                self._edsdk.disconnect()
                self._edsdk.terminate()
            except Exception:
                pass

        if self._opencv_cap:
            try:
                self._opencv_cap.release()
            except Exception:
                pass

        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    app = CanonWebcamApp()
    app.run()


if __name__ == "__main__":
    main()
