# Martin — mobile cartoon direction

Updated after user clarification: a lightweight cartoon character with textures
similar in complexity to Talking Tom is sufficient. Do not target film-quality fur.
Preserve Martin's identity, outfit and real-cat gray tabby coat; do not copy Tom's identity.

## Current implementation

- Unified face surface with recessed spherical eyes.
- No individual hair geometry, particles or fur simulation.
- One baked 1024×1024 coat atlas embedded in GLB.
- Parts consolidated by material, retaining bone vertex groups.
- Hard build caps: 40,000 triangles, 16 meshes, 8 MiB GLB.
- Four skeletal clips: Idle, Talk, Wave, DJ.

## Still required before production readiness

- Visual review of silhouette, eye placement, ears, clothing and coat.
- Smooth deformation weights instead of rigid prototype part weighting.
- Eyelid blinking and phoneme/mouth shape animation.
- Android integration and device measurement of frame time, memory and loading.
- Low-cost scene lighting and shadows selected in the Android renderer.

Build caps are engineering targets, NOT guaranteed FPS. Offline Cycles render times do not measure phone real-time performance.
Only real source/exported-model renders count as visual evidence.
Private reference photographs are not committed to this public repository.

## Verified build 33046323733

GLB: 2,212,088 bytes; 34,906 triangles; 10 meshes; one skin; four clips.
Baked atlas and reimport rendering passed. Eyes remain overly prominent.
Visual design and Android integration are not finished.
