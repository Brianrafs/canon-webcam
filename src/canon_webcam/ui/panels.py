"""Painéis da interface Tkinter (separados da lógica de aplicação)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from canon_webcam.domain.devices import CameraDevice


class ConnectionPanel(ttk.Frame):
    def __init__(
        self,
        parent,
        on_scan: Callable[[], None],
        on_connect: Callable[[], None],
        on_disconnect: Callable[[], None],
    ):
        super().__init__(parent)
        self._on_scan = on_scan
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect

        self._devices: List[CameraDevice] = []
        self._use_edsdk_var = tk.BooleanVar(value=False)
        self._mode_var = tk.StringVar(value="")
        self._status_var = tk.StringVar(value="Disconnected")
        self._device_var = tk.StringVar()

        self._build()
        self.set_connected(False)

    def _build(self) -> None:
        frame = self
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Camera Source", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        self._mode_label = ttk.Label(frame, textvariable=self._mode_var, style="Mode.TLabel")
        self._mode_label.pack(anchor=tk.W)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self._scan_btn = ttk.Button(btn_frame, text="Scan Devices", command=self._on_scan)
        self._scan_btn.pack(side=tk.LEFT, padx=(0, 5))

        self._connect_btn = ttk.Button(btn_frame, text="Start", command=self._on_connect)
        self._connect_btn.pack(side=tk.LEFT, padx=(0, 5))

        self._disconnect_btn = ttk.Button(btn_frame, text="Stop", command=self._on_disconnect)
        self._disconnect_btn.pack(side=tk.LEFT)

        ttk.Checkbutton(
            frame, text="Scan via EDSDK (advanced)", variable=self._use_edsdk_var
        ).pack(anchor=tk.W, pady=(4, 0))

        self._device_combo = ttk.Combobox(frame, state="readonly", width=35, textvariable=self._device_var)
        self._device_combo.pack(fill=tk.X, pady=2)

    # ------------------------------------------------------------------
    @property
    def use_edsdk(self) -> bool:
        return self._use_edsdk_var.get()

    def set_devices(self, devices: List[CameraDevice]) -> None:
        self._devices = devices
        values = [d.label for d in devices]
        self._device_combo["values"] = values
        if values:
            self._device_var.set(values[0])
        self._mode_var.set(f"Found {len(devices)} device(s)")

    def selected_device(self) -> Optional[CameraDevice]:
        current = self._device_combo.current()
        if 0 <= current < len(self._devices):
            return self._devices[current]
        return None

    def set_connected(self, connected: bool) -> None:
        self._connect_btn.config(state=tk.NORMAL if not connected else tk.DISABLED)
        self._disconnect_btn.config(state=tk.DISABLED if not connected else tk.NORMAL)
        self._scan_btn.config(state=tk.NORMAL if not connected else tk.DISABLED)

    def set_status(self, text: str) -> None:
        self._status_var.set(text)

    def set_mode(self, text: str) -> None:
        self._mode_var.set(text)

    @property
    def status_var(self) -> tk.StringVar:
        return self._status_var


class HudSettingsPanel(ttk.Frame):
    def __init__(
        self,
        parent,
        on_changed: Callable[[], None],
        on_apply_crop: Callable[[], None],
        on_auto_detect: Callable[[], None],
    ):
        super().__init__(parent)
        self._on_changed = on_changed
        self._on_apply_crop = on_apply_crop
        self._on_auto_detect = on_auto_detect

        self._blur_var = tk.BooleanVar(value=True)
        self._crop_var = tk.BooleanVar(value=False)
        self._crop_x_var = tk.IntVar(value=0)
        self._crop_y_var = tk.IntVar(value=0)
        self._crop_w_var = tk.IntVar(value=0)
        self._crop_h_var = tk.IntVar(value=0)

        self._build()

    def _build(self) -> None:
        frame = self
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="HUD Control", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        ttk.Checkbutton(
            frame, text="Blur HUD areas", variable=self._blur_var, command=self._on_changed
        ).pack(anchor=tk.W, pady=2)

        ttk.Checkbutton(
            frame, text="Custom crop", variable=self._crop_var, command=self._on_changed
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

        ttk.Button(frame, text="Apply Crop", command=self._on_apply_crop).pack(fill=tk.X, pady=5)
        ttk.Button(frame, text="Auto Detect HUD", command=self._on_auto_detect).pack(fill=tk.X, pady=2)

    # ------------------------------------------------------------------
    def apply_to_processor(self, processor) -> None:
        processor.set_blur_hud(self._blur_var.get())
        processor.set_auto_crop_enabled(self._crop_var.get())

    def apply_crop_to_processor(self, processor) -> None:
        x = self._crop_x_var.get()
        y = self._crop_y_var.get()
        w = self._crop_w_var.get()
        h = self._crop_h_var.get()

        if w > 0 and h > 0:
            processor.set_crop_region(x, y, w, h)
            processor.set_auto_crop_enabled(True)
            self._crop_var.set(True)
            self.apply_to_processor(processor)

    def set_blur(self, enabled: bool) -> None:
        self._blur_var.set(enabled)


class CameraControlPanel(ttk.Frame):
    def __init__(
        self,
        parent,
        on_set_value: Callable[[str, str], None],
        on_focus_auto: Callable[[], None],
        on_focus_near: Callable[[], None],
        on_focus_far: Callable[[], None],
    ):
        super().__init__(parent)
        self._on_set_value = on_set_value
        self._on_focus_auto = on_focus_auto
        self._on_focus_near = on_focus_near
        self._on_focus_far = on_focus_far

        self._combos: dict = {}
        self._status_var = tk.StringVar(value="")

        self._build()
        self.set_enabled(False)

    def _build(self) -> None:
        frame = self
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Camera Controls", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(
            frame,
            text="Requires EDSDK connection\n(DirectShow mode cannot control the camera)",
            style="Status.TLabel",
            wraplength=280,
        ).pack(anchor=tk.W, pady=(0, 4))

        for key, label in (("iso", "ISO"), ("av", "Aperture (Av)"), ("tv", "Shutter (Tv)")):
            row = ttk.Frame(frame)
            row.pack(fill=tk.X, pady=1)
            ttk.Label(row, text=label, width=12).pack(side=tk.LEFT)
            combo = ttk.Combobox(row, state="readonly", width=11)
            combo.pack(side=tk.LEFT, expand=True, fill=tk.X)
            ttk.Button(
                row, text="Set", width=4,
                command=lambda k=key: self._on_set_value(k, self._combos[k].get()),
            ).pack(side=tk.LEFT, padx=(4, 0))
            self._combos[key] = combo

        focus_row = ttk.Frame(frame)
        focus_row.pack(fill=tk.X, pady=(5, 2))
        ttk.Button(focus_row, text="Auto Focus", command=self._on_focus_auto).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2)
        )
        ttk.Button(focus_row, text="Near", command=self._on_focus_near).pack(
            side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 2)
        )
        ttk.Button(focus_row, text="Far", command=self._on_focus_far).pack(
            side=tk.LEFT, expand=True, fill=tk.X
        )

        ttk.Label(frame, textvariable=self._status_var, style="Status.TLabel").pack(anchor=tk.W)

    # ------------------------------------------------------------------
    def populate(self, key: str, labels: List[str], current: Optional[str] = None) -> None:
        combo = self._combos.get(key)
        if combo is None:
            return
        combo["values"] = labels
        combo.set(current if current and current in labels else (labels[0] if labels else ""))

    def get_value(self, key: str) -> str:
        return self._combos.get(key, ttk.Combobox).get() or ""

    def set_enabled(self, enabled: bool) -> None:
        state = "readonly" if enabled else "disabled"
        for combo in self._combos.values():
            combo.config(state=state)

    def set_status(self, text: str) -> None:
        self._status_var.set(text)


class OutputPanel(ttk.Frame):
    def __init__(self, parent, on_start: Callable[[], None], on_stop: Callable[[], None]):
        super().__init__(parent)
        self._on_start = on_start
        self._on_stop = on_stop

        self._res_var = tk.StringVar(value="1280x720")
        self._fps_var = tk.StringVar(value="30")

        self._build()
        self.set_running(False)

    def _build(self) -> None:
        frame = self
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Virtual Webcam Output", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)

        res_frame = ttk.Frame(frame)
        res_frame.pack(fill=tk.X, pady=2)
        ttk.Label(res_frame, text="Resolution:").pack(side=tk.LEFT)
        ttk.Combobox(
            res_frame, values=["640x480", "1280x720", "1920x1080"],
            width=12, state="readonly", textvariable=self._res_var,
        ).pack(side=tk.RIGHT)

        fps_frame = ttk.Frame(frame)
        fps_frame.pack(fill=tk.X, pady=2)
        ttk.Label(fps_frame, text="FPS:").pack(side=tk.LEFT)
        ttk.Combobox(
            fps_frame, values=["24", "25", "30", "60"],
            width=12, state="readonly", textvariable=self._fps_var,
        ).pack(side=tk.RIGHT)

        self._start_btn = ttk.Button(frame, text="Start Virtual Cam", command=self._on_start)
        self._start_btn.pack(fill=tk.X, pady=(5, 2))

        self._stop_btn = ttk.Button(frame, text="Stop Virtual Cam", command=self._on_stop)
        self._stop_btn.pack(fill=tk.X)

    # ------------------------------------------------------------------
    @property
    def resolution(self) -> tuple:
        w, _, h = self._res_var.get().partition("x")
        return (int(w), int(h))

    @property
    def fps(self) -> int:
        return int(self._fps_var.get())

    def set_running(self, running: bool) -> None:
        self._start_btn.config(state=tk.DISABLED if running else tk.NORMAL)
        self._stop_btn.config(state=tk.NORMAL if running else tk.DISABLED)


class InfoPanel(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._battery_var = tk.StringVar(value="Battery: --")
        self._fps_var = tk.StringVar(value="FPS: 0")
        self._res_var = tk.StringVar(value="--")

        frame = self
        frame.pack(fill=tk.X)

        ttk.Label(frame, text="Info", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._battery_var, style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._fps_var, style="Status.TLabel").pack(anchor=tk.W)
        ttk.Label(frame, textvariable=self._res_var, style="Status.TLabel").pack(anchor=tk.W)

    # ------------------------------------------------------------------
    def set_battery(self, text: str) -> None:
        self._battery_var.set(text)

    def set_fps(self, fps: float) -> None:
        self._fps_var.set(f"FPS: {fps:.1f}")

    def set_resolution(self, text: str) -> None:
        self._res_var.set(text)