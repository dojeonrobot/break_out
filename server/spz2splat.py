import gzip, struct, sys, numpy as np
def convert(src, dst):
    raw = gzip.decompress(open(src,'rb').read())
    magic, ver, n, shd, fb, flags, _ = struct.unpack_from('<IIIBBBB', raw, 0)
    assert magic == 0x5053474e, hex(magic)
    o = 16
    pos = np.frombuffer(raw, np.uint8, n*9, o).reshape(n,3,3).astype(np.int32); o += n*9
    p = pos[:,:,0] | (pos[:,:,1]<<8) | (pos[:,:,2]<<16)
    p = np.where(p & 0x800000, p - (1<<24), p).astype(np.float32) / (1<<fb)
    a = np.frombuffer(raw, np.uint8, n, o); o += n
    c = np.frombuffer(raw, np.uint8, n*3, o).reshape(n,3).astype(np.float32); o += n*3
    s = np.frombuffer(raw, np.uint8, n*3, o).reshape(n,3).astype(np.float32); o += n*3
    if ver >= 3:
        r = np.frombuffer(raw, np.uint8, n*4, o).reshape(n,4).astype(np.uint32); o += n*4
        comp = r[:,0] | (r[:,1]<<8) | (r[:,2]<<16) | (r[:,3]<<24)
        il = (comp >> 30).astype(np.int64)
        q = np.zeros((n,4), np.float32); mask = (1<<9)-1
        for i in range(3,-1,-1):
            sel = il != i
            mag = (comp & mask).astype(np.float32); neg = (comp >> 9) & 1
            v = np.sqrt(0.5) * mag / mask; v = np.where(neg==1, -v, v)
            q[sel, i] = v[sel]
            comp = np.where(sel, comp >> 10, comp)
        ss = (q**2).sum(1) - q[np.arange(n), il]**2
        q[np.arange(n), il] = np.sqrt(np.clip(1-ss, 0, 1))
    else:
        r = np.frombuffer(raw, np.uint8, n*3, o).reshape(n,3).astype(np.float32); o += n*3
        xyz = r/127.5 - 1
        q = np.concatenate([xyz, np.sqrt(np.clip(1-(xyz**2).sum(1,keepdims=True),0,1))], 1)
    # q is (x,y,z,w)
    scale = np.exp(s/16.0 - 10.0)
    dc = (c/255.0 - 0.5)/0.15
    rgb = np.clip((0.5 + 0.28209479*dc)*255, 0, 255).astype(np.uint8)
    qn = q / np.linalg.norm(q, axis=1, keepdims=True)
    rot = np.clip(np.stack([qn[:,3],qn[:,0],qn[:,1],qn[:,2]],1)*128+128, 0, 255).astype(np.uint8)
    order = np.argsort(-(scale.prod(1) * a/255.0))
    rec = np.zeros(n, dtype=[('p','<f4',3),('s','<f4',3),('c','u1',4),('r','u1',4)])
    rec['p'] = p[order]; rec['s'] = scale[order]
    rec['c'][:,:3] = rgb[order]; rec['c'][:,3] = a[order]; rec['r'] = rot[order]
    open(dst,'wb').write(rec.tobytes())
    return dict(version=ver, points=int(n), sh=shd, bbox=[p.min(0).round(3).tolist(), p.max(0).round(3).tolist()])
if __name__ == '__main__':
    print(convert(sys.argv[1], sys.argv[2]))
