from __future__ import annotations

import os

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.properties import NumericProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

import theme as T

TITLE_VARIANTS = (
    "crush_in",
    "scale_bloom",
    "fracture_sync",
    "bottom_rise",
)


def _asset_path(filename: str) -> str:
    return os.path.join(os.path.dirname(__file__), filename)


def _best_icon_source(preferred: str, fallback: str) -> str:
    preferred_path = _asset_path(preferred)
    if os.path.exists(preferred_path):
        return preferred_path
    return _asset_path(fallback)


class PsykeSplashArt(FloatLayout):
    fracture_scale = NumericProperty(0.52)
    head_scale = NumericProperty(0.92)
    impact_shift_x = NumericProperty(0.0)
    impact_shift_y = NumericProperty(0.0)

    def __init__(self, icon_size=dp(132), **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (icon_size, icon_size)

        self._base_size = float(icon_size)
        self._visual_center_shift_x = -dp(3.25)
        self._head_source = _best_icon_source("splash_head.png", "icon.png")
        self._fracture_source = _best_icon_source("splash_fracture.png", "icon.png")

        self._head = Image(
            source=self._head_source,
            size_hint=(None, None),
            opacity=0.0,
        )
        self._fracture = Image(
            source=self._fracture_source,
            size_hint=(None, None),
            opacity=0.0,
        )

        self.add_widget(self._head)
        self.add_widget(self._fracture)

        self.bind(
            pos=self._layout_layers,
            size=self._layout_layers,
            head_scale=self._layout_layers,
            fracture_scale=self._layout_layers,
            impact_shift_x=self._layout_layers,
            impact_shift_y=self._layout_layers,
        )
        Clock.schedule_once(lambda *_: self.reset_animation(), 0)

    def _layout_layers(self, *_):
        head_size = self._base_size * self.head_scale
        fracture_size = self._base_size * self.fracture_scale

        self._head.size = (head_size, head_size)
        self._head.pos = (
            self.x + (self.width - head_size) / 2 + self._visual_center_shift_x + self.impact_shift_x,
            self.y + (self.height - head_size) / 2 + self.impact_shift_y,
        )

        self._fracture.size = (fracture_size, fracture_size)
        self._fracture.pos = (
            self.x + (self.width - fracture_size) / 2 + self._visual_center_shift_x + self.impact_shift_x,
            self.y + (self.height - fracture_size) / 2 + self.impact_shift_y,
        )

    def reset_animation(self):
        Animation.cancel_all(self, "head_scale", "fracture_scale", "impact_shift_x", "impact_shift_y")
        Animation.cancel_all(self._head, "opacity")
        Animation.cancel_all(self._fracture, "opacity")

        self.head_scale = 0.92
        self.fracture_scale = 0.52
        self.impact_shift_x = 0.0
        self.impact_shift_y = 0.0
        self._head.opacity = 0.0
        self._fracture.opacity = 0.0
        self._layout_layers()

    def start_animation(self):
        self.reset_animation()

        head_in = Animation(head_scale=1.0, duration=0.34, t="out_cubic")
        head_glow = Animation(head_scale=1.03, duration=0.16, t="in_out_sine") + Animation(
            head_scale=1.0, duration=0.18, t="in_out_sine"
        )
        (head_in + head_glow).start(self)
        Animation(opacity=1.0, duration=0.22, t="out_quad").start(self._head)

        def _start_fracture(*_args):
            # Return to the earlier rhythm, with a slightly denser settle.
            fracture_burst = (
                Animation(fracture_scale=0.46, duration=0.08, t="out_quad")
                + Animation(fracture_scale=1.08, duration=0.24, t="out_expo")
                + Animation(fracture_scale=1.0, duration=0.18, t="out_cubic")
            )
            fracture_burst.start(self)
            impact_recoil = (
                Animation(impact_shift_x=dp(1), impact_shift_y=-dp(1), duration=0.06, t="out_quad")
                + Animation(impact_shift_x=-dp(3), impact_shift_y=dp(1), duration=0.11, t="out_quad")
                + Animation(impact_shift_x=0.0, impact_shift_y=0.0, duration=0.18, t="out_cubic")
            )
            head_recoil = (
                Animation(head_scale=0.992, duration=0.06, t="out_quad")
                + Animation(head_scale=1.015, duration=0.12, t="out_quad")
                + Animation(head_scale=1.0, duration=0.18, t="out_cubic")
            )
            impact_recoil.start(self)
            head_recoil.start(self)
            Animation(opacity=1.0, duration=0.12, t="out_quad").start(self._fracture)

        Clock.schedule_once(_start_fracture, 0.22)


class PsykeSplashLogo(FloatLayout):
    logo_scale_x = NumericProperty(0.80)
    logo_scale_y = NumericProperty(1.24)
    logo_shift_x = NumericProperty(0.0)
    logo_shift_y = NumericProperty(dp(30))

    def __init__(self, logo_width=dp(208), variant: str = "crush_in", **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (logo_width, dp(78))
        self._base_width = float(logo_width)
        self._base_height = float(dp(78))
        self._variant = variant if variant in TITLE_VARIANTS else "crush_in"
        self._logo = Image(
            source=_best_icon_source("splash_logo.png", "icon.png"),
            size_hint=(None, None),
            opacity=0.0,
        )
        self.add_widget(self._logo)
        self.bind(
            pos=self._layout_logo,
            size=self._layout_logo,
            logo_scale_x=self._layout_logo,
            logo_scale_y=self._layout_logo,
            logo_shift_x=self._layout_logo,
            logo_shift_y=self._layout_logo,
        )
        Clock.schedule_once(lambda *_: self.reset_animation(), 0)

    def _layout_logo(self, *_):
        width = self._base_width * self.logo_scale_x
        height = self._base_height * self.logo_scale_y
        self._logo.size = (width, height)
        self._logo.pos = (
            self.x + (self.width - width) / 2 + self.logo_shift_x,
            self.y + (self.height - height) / 2 + self.logo_shift_y,
        )

    def reset_animation(self):
        Animation.cancel_all(self, "logo_scale_x", "logo_scale_y", "logo_shift_x", "logo_shift_y")
        Animation.cancel_all(self._logo, "opacity")
        self.logo_scale_x = 1.0
        self.logo_scale_y = 1.0
        self.logo_shift_x = 0.0
        self.logo_shift_y = 0.0
        self._logo.opacity = 0.0
        self._layout_logo()

    def start_animation(self):
        self.reset_animation()
        if self._variant == "scale_bloom":
            self._start_scale_bloom()
        elif self._variant == "fracture_sync":
            self._start_fracture_sync()
        elif self._variant == "bottom_rise":
            self._start_bottom_rise()
        else:
            self._start_crush_in()

    def _start_crush_in(self):
        # Starts larger and dimmer, then crushes into place with a hard settle.
        self.logo_scale_x = 1.18
        self.logo_scale_y = 1.10
        self.logo_shift_y = 0.0
        self._layout_logo()
        self._logo.opacity = 0.58
        Animation(opacity=1.0, duration=0.20, t="out_quad").start(self._logo)
        (
            Animation(
                logo_scale_x=0.90,
                logo_scale_y=1.12,
                logo_shift_x=0.0,
                logo_shift_y=0.0,
                duration=0.22,
                t="out_expo",
            )
            + Animation(
                logo_scale_x=1.03,
                logo_scale_y=0.97,
                logo_shift_x=0.0,
                logo_shift_y=0.0,
                duration=0.12,
                t="out_quad",
            )
            + Animation(
                logo_scale_x=1.0,
                logo_scale_y=1.0,
                logo_shift_x=0.0,
                logo_shift_y=0.0,
                duration=0.18,
                t="out_cubic",
            )
        ).start(self)

    def _start_scale_bloom(self):
        # High-opacity large reveal that tightens down with one subtle recoil.
        self.logo_scale_x = 1.10
        self.logo_scale_y = 1.10
        self.logo_shift_y = 0.0
        self._layout_logo()
        self._logo.opacity = 0.92
        Animation(opacity=1.0, duration=0.16, t="out_quad").start(self._logo)
        (
            Animation(
                logo_scale_x=0.985,
                logo_scale_y=0.985,
                logo_shift_y=0.0,
                duration=0.24,
                t="out_cubic",
            )
            + Animation(
                logo_scale_x=1.015,
                logo_scale_y=1.015,
                logo_shift_y=0.0,
                duration=0.10,
                t="out_quad",
            )
            + Animation(
                logo_scale_x=1.0,
                logo_scale_y=1.0,
                logo_shift_y=0.0,
                duration=0.14,
                t="out_cubic",
            )
        ).start(self)

    def _start_fracture_sync(self):
        # Stays in place; just materializes with a tiny horizontal stretch-settle.
        self.logo_scale_x = 1.08
        self.logo_scale_y = 0.98
        self.logo_shift_y = 0.0
        self._layout_logo()
        self._logo.opacity = 0.0
        Animation(opacity=1.0, duration=0.14, t="out_quad").start(self._logo)
        (
            Animation(
                logo_scale_x=0.97,
                logo_scale_y=1.01,
                logo_shift_y=0.0,
                duration=0.12,
                t="out_expo",
            )
            + Animation(
                logo_scale_x=1.01,
                logo_scale_y=0.995,
                logo_shift_y=0.0,
                duration=0.10,
                t="out_quad",
            )
            + Animation(
                logo_scale_x=1.0,
                logo_scale_y=1.0,
                logo_shift_y=0.0,
                duration=0.10,
                t="out_cubic",
            )
        ).start(self)

    def _start_bottom_rise(self):
        # Short rise from below with resistance, then a firm lock-in.
        self.logo_scale_x = 0.97
        self.logo_scale_y = 1.03
        self.logo_shift_y = -dp(18)
        self._layout_logo()
        self._logo.opacity = 0.0
        Animation(opacity=1.0, duration=0.20, t="out_quad").start(self._logo)
        (
            Animation(
                logo_scale_x=1.02,
                logo_scale_y=0.99,
                logo_shift_y=dp(3),
                duration=0.26,
                t="out_cubic",
            )
            + Animation(
                logo_scale_x=0.995,
                logo_scale_y=1.01,
                logo_shift_y=dp(-1),
                duration=0.10,
                t="out_quad",
            )
            + Animation(
                logo_scale_x=1.0,
                logo_scale_y=1.0,
                logo_shift_y=0.0,
                duration=0.14,
                t="out_cubic",
            )
        ).start(self)


def _layout_stage(stage: FloatLayout, art: PsykeSplashArt, logo: PsykeSplashLogo, *_):
    cx = stage.center_x
    cy = stage.center_y - dp(2)
    art.center_x = cx
    art.center_y = cy + dp(46)
    logo.center_x = cx + dp(13)
    logo.center_y = cy - dp(63)


def build_launch_stage(title_variant: str = "crush_in") -> FloatLayout:
    stage = FloatLayout(size_hint=(1, 1))
    art = PsykeSplashArt(icon_size=dp(132))
    logo = PsykeSplashLogo(logo_width=dp(214), variant=title_variant)
    stage.add_widget(art)
    stage.add_widget(logo)
    stage._art = art
    stage._logo = logo
    stage.bind(
        pos=lambda *_: _layout_stage(stage, art, logo),
        size=lambda *_: _layout_stage(stage, art, logo),
    )
    Clock.schedule_once(lambda *_: _layout_stage(stage, art, logo), 0)
    Clock.schedule_once(lambda *_: art.start_animation(), 0.04)
    Clock.schedule_once(lambda *_: logo.start_animation(), 0.56)
    return stage


def build_launch_splash(_subtitle_text: str = "", title_variant: str = "crush_in") -> FloatLayout:
    splash = FloatLayout(size_hint=(1, 1), opacity=1.0)
    with splash.canvas.before:
        Color(*T.k(T.BG))
        splash._bg = Rectangle()
    splash.bind(
        pos=lambda *_: _sync_launch_splash(splash),
        size=lambda *_: _sync_launch_splash(splash),
    )

    stage = build_launch_stage(title_variant=title_variant)
    splash.add_widget(stage)
    splash._stage = stage
    Clock.schedule_once(lambda *_: _sync_launch_splash(splash), 0)
    return splash


def _sync_launch_splash(splash: FloatLayout, *_):
    if hasattr(splash, "_bg"):
        splash._bg.pos = splash.pos
        splash._bg.size = splash.size
