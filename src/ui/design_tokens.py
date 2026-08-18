"""
Design Tokens - BPO Financeiro
Sistema de tokens de design para aplicação desktop PySide6.
Baseado no design system "Trust & Authority" (Professional Navy + Blue CTA).
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class ColorMode(Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class ColorTokens:
    """Tokens de cor para um modo específico."""
    primary: str
    on_primary: str
    secondary: str
    accent: str
    background: str
    foreground: str
    muted: str
    border: str
    destructive: str
    ring: str
    success: str
    warning: str
    info: str


@dataclass(frozen=True)
class SpacingTokens:
    """Tokens de espaçamento (base 8dp)."""
    xs: int = 4
    sm: int = 8
    md: int = 16
    lg: int = 24
    xl: int = 32
    xxl: int = 48


@dataclass(frozen=True)
class RadiusTokens:
    """Tokens de border radius."""
    sm: int = 4
    md: int = 8
    lg: int = 12
    xl: int = 16


@dataclass(frozen=True)
class TypographyTokens:
    """Tokens de tipografia."""
    font_family_heading: str = "Calistoga"
    font_family_body: str = "Inter"
    font_family_mono: str = "JetBrains Mono"
    
    # Tamanhos em pontos (pt)
    h1: int = 32
    h2: int = 24
    h3: int = 20
    h4: int = 18
    body_lg: int = 16
    body: int = 14
    body_sm: int = 12
    caption: int = 11
    
    # Pesos
    weight_light: int = 300
    weight_normal: int = 400
    weight_medium: int = 500
    weight_semibold: int = 600
    weight_bold: int = 700


@dataclass(frozen=True)
class ShadowTokens:
    """Tokens de sombra/elevation."""
    sm: str = "0 1px 2px rgba(0, 0, 0, 0.05)"
    md: str = "0 4px 6px rgba(0, 0, 0, 0.1)"
    lg: str = "0 10px 15px rgba(0, 0, 0, 0.1)"
    xl: str = "0 20px 25px rgba(0, 0, 0, 0.15)"
    focus: str = "0 0 0 2px"


@dataclass(frozen=True)
class TransitionTokens:
    """Tokens de transição/animação."""
    fast: int = 150
    normal: int = 200
    slow: int = 300


# =============================================================================
# PALETAS POR MODO
# =============================================================================

LIGHT_COLORS = ColorTokens(
    primary="#0F172A",
    on_primary="#FFFFFF",
    secondary="#334155",
    accent="#0369A1",
    background="#F8FAFC",
    foreground="#020617",
    muted="#E8ECF1",
    border="#E2E8F0",
    destructive="#DC2626",
    ring="#0F172A",
    success="#059669",
    warning="#D97706",
    info="#0369A1",
)

DARK_COLORS = ColorTokens(
    primary="#F8FAFC",
    on_primary="#020617",
    secondary="#CBD5E1",
    accent="#38BDF8",
    background="#0F172A",
    foreground="#F8FAFC",
    muted="#1E293B",
    border="#334155",
    destructive="#EF4444",
    ring="#38BDF8",
    success="#34D399",
    warning="#FBBF24",
    info="#38BDF8",
)

SPACING = SpacingTokens()
RADIUS = RadiusTokens()
TYPOGRAPHY = TypographyTokens()
SHADOWS = ShadowTokens()
TRANSITIONS = TransitionTokens()


# =============================================================================
# HELPERS
# =============================================================================

def get_colors(mode: ColorMode) -> ColorTokens:
    """Retorna tokens de cor para o modo especificado."""
    return LIGHT_COLORS if mode == ColorMode.LIGHT else DARK_COLORS


def get_color(mode: ColorMode, token: str) -> str:
    """Retorna valor de um token de cor específico."""
    colors = get_colors(mode)
    return getattr(colors, token, colors.foreground)


def rgba(hex_color: str, alpha: float) -> str:
    """Converte hex para rgba string."""
    hex_color = hex_color.lstrip("#")
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"rgba({r}, {g}, {b}, {alpha})"


def get_shadow(mode: ColorMode, level: str = "md") -> str:
    """Retorna sombra adaptada ao modo (mais suave no dark)."""
    base = getattr(SHADOWS, level, SHADOWS.md)
    if mode == ColorMode.DARK:
        return base.replace("0.05", "0.2").replace("0.1", "0.3").replace("0.15", "0.4")
    return base


# =============================================================================
# SEMÂNTICOS PARA COMPONENTES
# =============================================================================

COMPONENT_COLORS = {
    "button_primary": {
        "bg": "accent",
        "text": "on_primary",
        "hover_opacity": 0.9,
        "pressed_opacity": 0.8,
    },
    "button_secondary": {
        "bg": "muted",
        "text": "foreground",
        "hover_opacity": 0.8,
        "pressed_opacity": 0.7,
    },
    "button_destructive": {
        "bg": "destructive",
        "text": "on_primary",
        "hover_opacity": 0.9,
        "pressed_opacity": 0.8,
    },
    "button_outline": {
        "bg": "transparent",
        "text": "accent",
        "border": "accent",
        "hover_bg": "accent",
        "hover_text": "on_primary",
    },
    "input": {
        "bg": "background",
        "text": "foreground",
        "placeholder": "secondary",
        "border": "border",
        "border_focus": "ring",
        "bg_disabled": "muted",
    },
    "card": {
        "bg": "muted",
        "border": "border",
        "shadow": "md",
    },
    "table": {
        "header_bg": "muted",
        "header_text": "foreground",
        "row_bg": "background",
        "row_alt_bg": "muted",
        "border": "border",
        "hover_bg": "accent",
        "hover_text": "on_primary",
    },
    "badge": {
        "success_bg": "success",
        "success_text": "on_primary",
        "warning_bg": "warning",
        "warning_text": "on_primary",
        "destructive_bg": "destructive",
        "destructive_text": "on_primary",
        "info_bg": "info",
        "info_text": "on_primary",
        "default_bg": "secondary",
        "default_text": "on_primary",
    },
    "tooltip": {
        "bg": "foreground",
        "text": "background",
    },
    "modal": {
        "overlay": "rgba(0, 0, 0, 0.5)",
        "bg": "background",
        "border": "border",
        "shadow": "xl",
    },
}


def get_component_colors(mode: ColorMode, component: str) -> Dict[str, Any]:
    """Resolve cores semânticas de componente para valores reais."""
    colors = get_colors(mode)
    template = COMPONENT_COLORS.get(component, {})
    resolved = {}
    
    for key, value in template.items():
        if isinstance(value, str) and value in colors.__dict__:
            resolved[key] = getattr(colors, value)
        elif isinstance(value, str) and value.startswith("rgba"):
            resolved[key] = value
        else:
            resolved[key] = value
    
    return resolved