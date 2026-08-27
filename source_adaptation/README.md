# Direct source-model adaptation

This workflow actually reads the user-supplied Judy Hopps 2.0 Blender scene.
It does not invoke the old procedural Martin builder. No third-party model
or source texture is committed to this public repository.

The input README identifies the source as noncommercial fanart. Preserve that
restriction and the original attribution. This is not a freely licensed
commercial character.

## Reproduce

Use Python 3.11, bpy 4.4.0 and numpy 1.26.4 in a separate environment.

```sh
python source_adaptation/adapt_source.py --source /path/to/source.blend --out /path/to/output
```

Embedded source scripts are not executed. The script retains the source rig
and meshes hidden, makes evaluated mesh copies, reshapes those copies into
a cat, reuses Fur_COL and Fabric_BUMP, and adds original DJ accessories.
The output is a saved Blender scene and a real Cycles render.

**The visible adaptation is currently static.** The source rig and facial keys
remain in the file but are not transferred to the adapted render meshes.
No GLB export, Android optimization, animation validation or 1:1 visual
approval is claimed. The outfit and feet still need further art direction.
