# Appearance

## Per-button colors

Each button has two independent color settings, accessible in the button editor:

- **Color** — background color of the tile
- **Text color** — color of the label

Both use a 40-color GNOME palette with a hex input field for custom values.

## Button size

**Preferences → Button Grid Layout → Button size**

| Size | Dimensions |
|------|-----------|
| Small | 80 × 80 px |
| Medium | 120 × 120 px |
| Large | 160 × 160 px |

## Show icon only / label only

In the button editor:

- **Hide label** — displays the icon only (useful for small buttons or well-known icons)
- **Hide icon** — displays the label only

## Button themes *(Pro)*

!!! tip "Pro feature"
    Button themes require [Commandeck Pro](pro.md).

**Preferences → Button Appearance → Button theme**

| Theme | Style |
|-------|-------|
| Bold | Solid colored tiles with strong contrast (default) |
| Phone keys | Compact flat tiles, reminiscent of a dial pad |
| Neon | Dark background with glowing accent borders |
| Retro | Terminal-inspired monochrome with scanlines |

![Neon theme](assets/theme-neon.png){ width=49% } ![Retro theme](assets/theme-retro.png){ width=49% }

### Custom CSS *(Pro)*

Write your own stylesheet targeting the button tile for full control. Commandeck uses **Qt
Style Sheets (QSS)** — CSS-like, but with Qt selectors and gradients:

```css
QFrame#ButtonTile {
  background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                              stop:0 #6a0dad, stop:1 #9b30d9);
  border-radius: 12px;
  border: 2px solid rgba(255,255,255,0.2);
}

QFrame#ButtonTile:hover {
  border-color: rgba(255,255,255,0.6);
}

QFrame#ButtonTile QLabel#TileLabel {
  color: #ffffff;
  font-weight: bold;
}
```

Load it via **Preferences → Button Appearance → Custom CSS file → Browse**. Use the **Export template** button to get a starter file with all available selectors and named colors. See [Themes → Custom CSS](pro/themes.md#custom-css) for the full list of targets and QSS limitations.

## Color scheme

**Preferences → Interface → Color scheme**

- **Follow system** — respects your desktop dark/light setting
- **Light** — always light
- **Dark** — always dark
