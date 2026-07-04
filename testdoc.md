# Photo Workspace

A local-first photo layout workspace for arranging images on a large canvas and exporting them in visual order.

Photo Workspace is built for workflows where the order of images matters: contact-sheet planning, visual sequencing, shortlist review, and manual photo arrangement. Create projects, drop images onto a canvas, move and resize them, then export the original files with numbered filenames based on the layout.

## Features

- Create, rename, preview, and delete projects from the landing page
- Drag and drop or paste images into a project workspace
- Import up to 30 images at once
- Arrange photos on a scrollable, expanding dot-grid canvas
- Select multiple images with drag selection
- Move selected images together as a group
- Select all photos with `Ctrl+A` or `Cmd+A`
- Delete selected photos from the workspace
- Resize images while preserving aspect ratio
- Store project metadata locally without duplicating original image files
- Persist thumbnails separately for faster project reopening
- Refresh unavailable thumbnails when local file access changes
- Export original images as a numbered ZIP in visual layout order
- Generate HEIC thumbnails on macOS with a local helper and browser fallback

## Tech Stack

- React
- Vite
- Konva / react-konva
- IndexedDB for local project and thumbnail metadata
- File System Access API where supported
- macOS `sips` helper for HEIC thumbnail generation during development

## Getting Started

Use the Node version defined by `.nvmrc`:

```bash
nvm install
nvm use
```

This project currently uses Node `20`. If you do not use `nvm`, install a compatible Node.js version before continuing.

Install dependencies:

```bash
npm install
```

Start the app:

```bash
npm run dev
```

This starts:

- Vite app server at `http://localhost:5173/`
- Local thumbnail helper at `http://127.0.0.1:4174`

For Vite only:

```bash
npm run dev:vite
```

For the thumbnail helper only:

```bash
npm run dev:thumbs
```

Create a production build:

```bash
npm run build
```

Preview the production build:

```bash
npm run preview
```

## How To Use

1. Open the app and create a project.
2. Open the project workspace.
3. Drop or paste photos onto the canvas.
4. Arrange photos by dragging, selecting, grouping, and resizing.
5. Export the workspace when the layout is ready.

The export uses the original image files where available, so thumbnails and in-app preview quality do not reduce exported image quality.

## Storage Model

Photo Workspace is local-first. Project data is stored in the browser, not in this repository.

The app stores:

- Project metadata in IndexedDB
- Image positions, dimensions, ordering data, and project settings
- Thumbnail blobs for faster reloads
- File and directory handles when the browser supports them

The app does not intentionally duplicate full-resolution original images into IndexedDB. Instead, it keeps references to local files where possible and uses those originals during export.

Because projects live in browser storage, cloning this repo will not include another user's projects, thumbnails, file handles, or local images.

## HEIC Support

HEIC previews are difficult to handle consistently in browsers. During development, `npm run dev` starts a local thumbnail helper that uses macOS `sips` to generate JPEG thumbnails for HEIC files.

If the helper is unavailable or the platform does not support `sips`, the app falls back to browser-based HEIC conversion with `heic2any`.

If thumbnails fail because local file permissions changed, use the thumbnail refresh control in the workspace. Some browsers may also require reselecting or reauthorizing the source directory.

## Export Behavior

Export produces a ZIP containing numbered image files. Numbering is based on the visual arrangement of photos in the workspace, using the canvas layout as the source of truth.

Exported files preserve the original image data where the original local file is still accessible. The app may use smaller thumbnails for display performance, but those previews are not used as the final exported images.

## Browser Notes

The app works best in Chromium-based browsers because local file and directory handles are better supported there. Other browsers may still support drag-and-drop imports, but project reopening and export access can be more limited.

## Project Structure

```text
src/
  App.jsx
  main.jsx
  canvas/
    PhotoNode.jsx
    WorkspaceCanvas.jsx
  pages/
    LandingPage.jsx
    WorkspacePage.jsx
    landing/
      ProjectCard.jsx
  services/
    exportProject.js
    imageImport.js
    projectPersistence.js
  state/
    projectStore.jsx
  styles/
    global.css
scripts/
  dev.mjs
  thumbnailServer.mjs
FUNCTIONAL_SPEC.md
```

## Functional Spec

The product requirements and behavior notes live in [FUNCTIONAL_SPEC.md](./FUNCTIONAL_SPEC.md).

## License

ISC
