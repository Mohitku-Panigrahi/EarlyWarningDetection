---
name: Academic Intelligence Interface
colors:
  surface: '#f8f9ff'
  surface-dim: '#cedbf1'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff3ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dde9ff'
  surface-container-highest: '#d7e3fa'
  on-surface: '#101c2c'
  on-surface-variant: '#43474f'
  inverse-surface: '#253142'
  inverse-on-surface: '#ebf1ff'
  outline: '#737780'
  outline-variant: '#c3c6d0'
  surface-tint: '#3f5f8e'
  primary: '#00254c'
  on-primary: '#ffffff'
  primary-container: '#173b68'
  on-primary-container: '#87a6da'
  inverse-primary: '#a8c8fd'
  secondary: '#296199'
  on-secondary: '#ffffff'
  secondary-container: '#90c1ff'
  on-secondary-container: '#0d4f86'
  tertiary: '#002c1b'
  on-tertiary: '#ffffff'
  tertiary-container: '#00442c'
  on-tertiary-container: '#5bb68b'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d5e3ff'
  primary-fixed-dim: '#a8c8fd'
  on-primary-fixed: '#001b3b'
  on-primary-fixed-variant: '#264775'
  secondary-fixed: '#d2e4ff'
  secondary-fixed-dim: '#a0c9ff'
  on-secondary-fixed: '#001c37'
  on-secondary-fixed-variant: '#00497f'
  tertiary-fixed: '#99f5c6'
  tertiary-fixed-dim: '#7dd8ab'
  on-tertiary-fixed: '#002113'
  on-tertiary-fixed-variant: '#005236'
  background: '#f8f9ff'
  on-background: '#101c2c'
  surface-variant: '#d7e3fa'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 36px
    fontWeight: '600'
    lineHeight: 44px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0em
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  data-tabular:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-tablet: 1.5rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2rem
---

## Brand & Style

This design system serves faculty, researchers, and students navigating complex higher-education workflows, degree progression, grant management, and daily academic habits. The visual identity merges the systematic rigor of developer tools (Linear), the modular focus of document-driven environments (Notion), and the data precision of financial interfaces (Stripe).

The aesthetic is strictly **Modern Academic Functionalism**:
- **Clarity over ornamentation**: Absolute rejection of neon accents, heavy frosted glassmorphism, aggressive gradients, and decorative animations.
- **Data-first density**: Telemetry, course metrics, cohort performance, and audit trails demand compact, scannable hierarchies.
- **Calm, institutional authority**: Deep navy conveys institutional permanence, balanced against structured white modules and neutral slate backgrounds to reduce cognitive fatigue during prolonged working sessions.

## Colors

The system relies on a restrained palette engineered for contrast, legibility, and high-density information displays.

- **Primary Canvas (`#F5F7FA`)**: Soft cool gray base that prevents glare while setting off white content cards without harsh contrast.
- **Surface / Card (`#FFFFFF`)**: Pure white containers anchoring telemetry, grids, tables, and workspaces.
- **Primary Navy (`#173B68`)**: Anchors focal elements, primary actions, critical state indicators, and active navigation bars.
- **Secondary Blue (`#477BB5`)**: Supporting interactive accents, focused states, linked resources, and progressive indicators.
- **Success Green (`#23845D`)**: Used for completed credits, passing thresholds, verified submissions, and positive metric deltas.
- **Warning Amber (`#D49B3D`)**: Highlights attendance warnings, pending thesis reviews, and approaching project deadlines.
- **Text Primary (`#263548`)**: High-contrast, slate-tinted dark charcoal ensuring WCAG AAA legibility across body text and tabular figures.
- **Text Secondary (`#778397`)**: Muted slate for metadata, subheadings, keyboard shortcuts, and empty states.
- **Structural Border (`#E2E8F0`)**: Crisp 1px boundary lines dividing tables, cards, toolbars, and input fields.

## Typography

Inter handles all typographic requirements across the dashboard.

- **Tabular Numerals**: Apply `font-feature-settings: "tnum" 1, "cv05" 1, "cv11" 1` across all habit tracking matrices, GPA calculations, course credit breakdowns, and calendar grids to ensure numbers align vertically without jitter.
- **Letter Spacing**: Tighter negative tracking (`-0.02em` to `-0.025em`) is enforced on headlines to maintain high cohesion at large sizes. Sub-labels and uppercase status tags require generous tracking (`+0.04em`) to ensure legibility at micro scales (11px).
- **Hierarchy Rules**: Display headings are restricted to global dashboard overviews; modular card headers use `headline-sm` or `headline-md` to preserve vertical real estate.

## Layout & Spacing

The layout model is anchored to a strict 8px grid system (with a 4px half-step for micro alignments such as icon-label pairings and table cell padding).

### Layout System
- **Desktop (≥1280px)**: 12-column fluid grid inside a 1440px max-width boundary. Side navigation uses a fixed 240px rail with an optional collapsed 64px state. Outer margin: `margin-desktop` (32px), column gutter: `gutter-desktop` (24px).
- **Tablet (768px - 1279px)**: 8-column layout. Sidebar collapses to an icon rail or sheet drawer. Margins step down to `margin-tablet` (24px), gutters to `gutter` (16px).
- **Mobile (≤767px)**: 4-column layout with horizontal stacking. Telemetry cards collapse from multi-column grids to swipeable carousels or single-column summary stacks. Margin: `margin` (16px), gutters: 12px.

### Density & Rhythms
Spacing tokens are used strictly for layout separation:
- `space-xs` (4px): Chip padding, inline icon-to-label gaps, habit tracking day-cell spacing.
- `space-sm` (8px): Stacked text metadata, form input vertical padding, sub-item lists.
- `space-md` (16px): Card interior padding, metric row gaps, filter bar item spacing.
- `space-lg` (24px): Inter-card spacing within dashboard rows, section divider spacing.
- `space-xl` (32px): Primary dashboard canvas section gaps and page title separations.

## Elevation & Depth

Visual hierarchy relies on crisp borders and low-spread, ambient shadows rather than elevation through blur or z-axis drama.

- **Primary Structure**: Every card, panel, and data row relies on a crisp `1px solid #E2E8F0` border.
- **Ambient Card Shadows**: Elevated cards use a double-layer, micro-blur shadow: `0 1px 3px rgba(23, 59, 104, 0.04), 0 1px 2px rgba(23, 59, 104, 0.02)`. This tethers elements to the `#F5F7FA` canvas without creating artificial floating planes.
- **Hover & Active States**: Interactive cards and row items transition smoothly to `0 4px 6px -1px rgba(23, 59, 104, 0.06), 0 2px 4px -1px rgba(23, 59, 104, 0.03)` with a subtle border darkening to `#CBD5E1`.
- **Flyouts & Menus**: Popovers, command palettes, and dropdown menus utilize a focused shadow: `0 10px 15px -3px rgba(23, 59, 104, 0.08), 0 4px 6px -2px rgba(23, 59, 104, 0.03)` combined with a `1px solid #E2E8F0` border.
- **No Diffusion**: Blurs exceeding 16px are strictly disallowed to maintain crisp academic precision.

## Shapes

The interface utilizes a compact, refined shape hierarchy (`roundedness: 1`):

- **Default Radius (4px / 0.25rem)**: Base inputs, buttons, status chips, dropdown triggers, and habit calendar activity cells.
- **Container Radius (8px / 0.5rem - `rounded-lg`)**: Metrics cards, data tables, telemetry panels, modal dialogs, and navigation drawers.
- **Pill Exception**: Circular tags (`rounded-full`) are reserved exclusively for user avatars and high-visibility status pips (e.g., live lecture indicators, active sync pings).

## Components

### Buttons
- **Primary**: Solid background `#173B68`, text `#FFFFFF`, 4px border radius. Hover: `#1E4B82`. Active: `#122D50`. Focus: 2px ring `#477BB5` offset by 2px white.
- **Secondary**: Background `#FFFFFF`, 1px border `#E2E8F0`, text `#263548`. Hover: `#F5F7FA` with border `#CBD5E1`.
- **Subtle / Ghost**: Transparent background, text `#778397`. Hover: `#F5F7FA`, text `#263548`.
- **Sizing**: Default height 36px (14px font, 12px horizontal padding); compact height 28px (12px font, 8px horizontal padding) for dense table operations.

### Cards & Telemetry Panels
- Surface: `#FFFFFF` encased in 1px `#E2E8F0` border with 8px radius (`rounded-lg`).
- Internal layout: Structured header (title in `label-md` `#778397` uppercase, right-aligned action icon), prominent numeric display (`headline-lg` `#263548` with tabular numbers), and contextual delta badge (`+2.4% vs last semester`).
- Padding: 16px desktop, 12px mobile.

### Academic Telemetry & Habit Tracking Grids
- **Matrix Layout**: Compact 7-column or 52-week horizontal calendar grids inspired by developer contribution graphs.
- **Cells**: 12px × 12px squares with 3px border radius and 2px gap (`space-xs`).
- **Intensity Mapping**:
  - Inactive / None: `#E2E8F0`
  - Level 1 (1–2 hrs study / completed tasks): Tinted secondary `#D5E3F2`
  - Level 2 (3–4 hrs): Mid secondary `#8EB2D8`
  - Level 3 (5+ hrs): Full secondary `#477BB5`
  - Goal Met / Milestone: Primary navy `#173B68` or success `#23845D`
- **Tooltips**: Instant-render tooltip on cell hover showing timestamp, academic module, and activity score.

### Tables & Course Rosters
- Striping: Flat white rows with `1px solid #E2E8F0` bottom divider. Hover row highlight: `#F8FAFC`.
- Header: `#F5F7FA` background, 32px height, 11px uppercase `label-sm` in `#778397`, left-aligned for strings, right-aligned for numbers and dates.
- Cells: 40px compact row height, vertical centering, text in `data-tabular` `#263548`.

### Chips & Badges
- **Status Badges**: Pill-shaped or 4px radius, 20px height, 6px horizontal padding.
  - Active / Success: Background `#E8F4EE`, text `#23845D`, border `1px solid #C4E3D3`.
  - Pending / Warning: Background `#FAF4E8`, text `#D49B3D`, border `1px solid #F3DFB9`.
  - Neutral / Inactive: Background `#F1F5F9`, text `#778397`, border `1px solid #E2E8F0`.

### Form Fields & Inputs
- Height: 36px standard. Border: `1px solid #E2E8F0`, radius: 4px.
- Background: `#FFFFFF`. Text: `#263548`, placeholder: `#778397`.
- Focus state: Border color changes to `#477BB5` with a subtle `box-shadow: 0 0 0 1px #477BB5`. No heavy glowing outlines.
- Checkboxes: 16px × 16px square with 3px corner radius. Unchecked: `1px solid #CBD5E1`. Checked: `#173B68` background with crisp white check mark icon.