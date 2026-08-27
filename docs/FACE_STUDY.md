# Facial study and original Martin v04

The user supplied a third-party Blender character for studying construction.
Its internal README restricts commercial use. No geometry, rig, images, scripts,
or other bytes from that asset are imported into this repository or Martin.

The inspected file separates eyes/cornea, has facial corrective shape keys,
packed color/bump images, and extensive rig controls. These are general
techniques, not a source asset license for this project.

Original changes authored here:

- Annular quad eyelids with independent Blink.L and Blink.R morph targets.
- A Blink animation exported using glTF morph weights, without Blender drivers.
- Smaller recessed eyes, triangular ear inserts and a beveled triangular nose.
- A cheek Smile target; this is not a complete speech/phoneme system.
- A shared 256px fabric tangent-space normal map and tiled garment UVs.
- Export checks for morph names, target sizes, weight animation and normal map.
- Actual reimport renders of neutral and blink/smile expressions.

These changes do not fix all prototype limitations: body weights remain simple,
mouth opening is still driven by the prototype jaw bone, and Android performance
has not been measured. A visual inspection of eyelid closure is required after
every change; passing structural checks alone is not visual acceptance.

## Verified v04 build

Commit: 16a196f1d12c220206c01345d591e1988e2e0756.
GitHub Actions run: 33066460525 (all steps passed).

- GLB: 2,590,424 bytes, 33,746 triangles, 9 meshes, 1 skin.
- Clips: Blink, DJ, Idle, Talk, Wave. Targets: Blink.L, Blink.R, Smile.
- Packed maps: 1024px coat, 512px original iris, 256px fabric normal.
- Neutral and simultaneous blink/smile renders inspected after GLB reimport.
- Extra binary accessor check: 527 exported vertices move for blinking; zero
  overlap with the Smile target (previous iteration incorrectly shared 120).
- Validator rejects removal of Blink or the fabric normal map.

Visual limitations remain: visible outer eyelid seams, lumpy cheek transitions,
primitive torso/sleeves/shoes, and limited mouth articulation. This is a working
facial prototype, not an approved 1:1 likeness or a production-ready character.
No target Android device performance measurements have been made.
