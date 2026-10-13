# Dictation Notes web design

Updated 2026-10-13 following the user's request for a carefully designed light website. The tokens in `styles.css` are authoritative.

## Overview

All product, support, privacy, terms and error pages use a bright cool-white canvas, blue accents, generous whitespace and real application images. This connects the website to the native Mac interface and waveform icon.

**The Daylight Rule.** Every page and language stays light, including system controls, menus and sharing artwork.

## Colors

Use the shared canvas, surface, panel, ink, muted text, accent, hover and line tokens. Blue identifies actions and a few key labels; dark ink carries headings. Muted text must retain at least 4.5:1 contrast on its surface.

**The Quiet Accent Rule.** Screenshots explain the app; blue guides actions without decorating every paragraph.

## Typography

System sans-serif display gives headings the clarity of a native Mac window. Atkinson Hyperlegible is the body face, with system CJK and other script fallbacks. IBM Plex Mono is reserved for versions and keyboard shortcuts. Body is 16px with 1.75 line height; leads are 20px. The page container and 75ch prose limit prevent wide text walls.

**The Reading Rule.** Long words can wrap in every language, and document text remains readable at mobile width and zoom.

## Elevation

The interface is flat. Borders and pale surfaces separate menus, tables and real screenshot frames. Buttons and media have gently curved 8px corners; keyboard keys use 4px. No decorative shadows or gradients.

## Components

The shared header keeps four direct navigation choices and a native language disclosure. Primary downloads use blue buttons; the second platform uses a quiet surface button. Keyboard focus is visible, and Escape closes the language menu. FAQ answers remain visible for reading and crawling. Document topic links use an open grid; content uses clear headings, horizontal separators and generous paragraph spacing.

**The Real Screen Rule.** Use real localized app captures and explicitly identify demonstration conversations. Never assemble pretend product controls as a screenshot.

## Do's and don'ts

Use at least four layout patterns on the long product page, keep touch targets at least 44px, and test 375/768/1440px with Arabic RTL. Preserve the screenshot aspect ratios and the complete text at every size.

Avoid generic AI subscription landing pages, invented testimonials or ratings, fabricated product screenshots, and unconditional offline or zero-retention promises. Avoid decorative blobs, card grids for simple prose, and theme changes between sections.
