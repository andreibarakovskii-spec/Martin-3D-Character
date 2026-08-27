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
