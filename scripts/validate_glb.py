"""Structural checks, not a replacement for the Khronos validator."""
import json
import struct
import sys
from pathlib import Path

def validate(path):
    raw=Path(path).read_bytes()
    magic,version,length=struct.unpack_from('<4sII',raw)
    assert magic==b'glTF' and version==2 and length==len(raw)
    pos=12; chunks=[]
    while pos < length:
        n,kind=struct.unpack_from('<II',raw,pos);pos+=8
        assert n%4==0 and pos+n<=length
        chunks.append((kind,raw[pos:pos+n]));pos+=n
    assert chunks[0][0]==0x4E4F534A
    doc=json.loads(chunks[0][1]); binary=next(data for kind,data in chunks if kind==0x004E4942)
    assert doc['asset']['version']=='2.0'
    assert doc.get('meshes') and doc.get('skins'),'Missing mesh or skin'
    assert all('uri' not in b for b in doc['buffers'])
    for v in doc['bufferViews']:
        assert v.get('byteOffset',0)+v['byteLength']<=len(binary)
    names={a.get('name') for a in doc.get('animations',[])}
    assert {'Idle','Talk','Wave','DJ'}<=names, f'Missing animations: {names}'
    triangles=0
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            assert p.get('mode',4)==4
            assert 'POSITION' in p['attributes']
            assert 'JOINTS_0' in p['attributes'] and 'WEIGHTS_0' in p['attributes']
            triangles+=doc['accessors'][p['indices']]['count']//3
    for a in doc['animations']:
        assert a['channels'] and a['samplers']
        for s in a['samplers']:
            acc=doc['accessors'][s['input']]
            assert acc['max'][0]>acc['min'][0]
    assert any('COLOR_0' in p['attributes'] for m in doc['meshes'] for p in m['primitives'])
    report={'status':'structural_checks_passed','bytes':len(raw),'triangles':triangles,
            'meshes':len(doc['meshes']),'skins':len(doc['skins']),'animations':sorted(names),
            'visual_likeness':'NOT VALIDATED','android_device':'NOT TESTED'}
    Path(path).with_suffix('.report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':validate(sys.argv[1])
