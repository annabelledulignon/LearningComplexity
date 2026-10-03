// Draws the stelae field of the Memorial to the Murdered Jews of Europe
// (Berlin) as faint grey blocks in perspective. Deterministic: the same
// field is drawn for every slide, seen from a camera that walks along it.
(function () {
  function hash(i, j) {
    let h = (Math.imul(i, 374761393) + Math.imul(j, 668265263)) | 0;
    h = Math.imul(h ^ (h >>> 13), 1274126177);
    h ^= h >>> 16;
    return (h >>> 0) / 4294967296;
  }
  function noise(x, z) {
    const xi = Math.floor(x), zi = Math.floor(z);
    const s = t => t * t * (3 - 2 * t);
    const u = s(x - xi), v = s(z - zi);
    const a = hash(xi, zi), b = hash(xi + 1, zi), c = hash(xi, zi + 1), d = hash(xi + 1, zi + 1);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  }
  const smooth = t => { t = Math.max(0, Math.min(1, t)); return t * t * (3 - 2 * t); };

  // Real dimensions in metres: stelae 0.95 x 2.38, aisles 0.95.
  const SW = 0.95, SL = 2.38, GAP = 0.95;
  const PX = SW + GAP, PZ = SL + GAP;

  function ground(i, j) {
    return -1.2 * smooth(j / 9) + 0.35 * Math.sin(i * 0.37 + 0.6) * Math.cos(j * 0.29);
  }
  function height(i, j) {
    const rise = smooth((j + 1) / 5);
    return 0.3 + rise * (2.4 + 2.3 * noise(i * 0.31 + 7, j * 0.33 + 3)) + 0.25 * hash(i, j);
  }

  window.drawStelae = function (canvas, opts) {
    const o = Object.assign({ walk: 0, alpha: 1, camY: 9, camZ: -6, yaw: 0.42, pitch: 0.5, f: 880, horizon: 0.5 }, opts || {});
    const W = canvas.width, H = canvas.height;
    // Draw opaque offscreen, then lay it down at the requested alpha, so
    // overlapping faces do not show through each other.
    const off = document.createElement('canvas');
    off.width = W; off.height = H;
    const ctx = off.getContext('2d');
    const cam = { x: o.walk, y: o.camY, z: o.camZ };
    const cy = Math.cos(o.yaw), sy = Math.sin(o.yaw), cp = Math.cos(o.pitch), sp = Math.sin(o.pitch);

    function proj(x, y, z) {
      const dx = x - cam.x, dy = y - cam.y, dz = z - cam.z;
      const x1 = dx * cy - dz * sy, z1 = dx * sy + dz * cy;
      const y2 = dy * cp + z1 * sp, z2 = -dy * sp + z1 * cp;
      return [W / 2 + o.f * x1 / z2, H * o.horizon - o.f * y2 / z2, z2];
    }

    const BG = [12, 12, 13];
    const boxes = [];
    const i0 = Math.floor(cam.x / PX) - 46, i1 = i0 + 92;
    for (let j = -4; j < 34; j++) {
      for (let i = i0; i < i1; i++) {
        const x0 = i * PX, z0 = j * PZ;
        const g = ground(i, j), top = g + height(i, j);
        const cx = x0 + SW / 2 - cam.x, cz = z0 + SL / 2 - cam.z;
        boxes.push({ x0, x1: x0 + SW, z0, z1: z0 + SL, y0: g, y1: top, d: Math.hypot(cx, top - cam.y, cz) });
      }
    }
    boxes.sort((a, b) => b.d - a.d);

    // Light from the upper left, slightly behind the viewer.
    const L = [-0.55, 0.7, -0.45];
    const shade = (n, base) => base * (0.55 + 0.45 * Math.max(0, n[0] * L[0] + n[1] * L[1] + n[2] * L[2]));

    ctx.lineJoin = 'round';
    for (const b of boxes) {
      const P = {
        a: proj(b.x0, b.y1, b.z0), b: proj(b.x1, b.y1, b.z0), c: proj(b.x1, b.y1, b.z1), d: proj(b.x0, b.y1, b.z1),
        e: proj(b.x0, b.y0, b.z0), f: proj(b.x1, b.y0, b.z0), g: proj(b.x1, b.y0, b.z1), h: proj(b.x0, b.y0, b.z1),
      };
      if (Object.values(P).some(p => p[2] < 0.4)) continue;
      const fog = Math.exp(-b.d / 55);
      const faces = [];
      if (cam.z < b.z0) faces.push([[P.e, P.f, P.b, P.a], [0, 0, -1], 70]);
      if (cam.z > b.z1) faces.push([[P.h, P.g, P.c, P.d], [0, 0, 1], 70]);
      if (cam.x < b.x0) faces.push([[P.e, P.h, P.d, P.a], [-1, 0, 0], 70]);
      if (cam.x > b.x1) faces.push([[P.f, P.g, P.c, P.b], [1, 0, 0], 70]);
      if (cam.y > b.y1) faces.push([[P.a, P.b, P.c, P.d], [0, 1, 0], 84]);
      for (const [pts, n, base] of faces) {
        const v = shade(n, base);
        const col = BG.map(c => Math.round(c + (v - c) * fog));
        ctx.beginPath();
        ctx.moveTo(pts[0][0], pts[0][1]);
        for (let k = 1; k < pts.length; k++) ctx.lineTo(pts[k][0], pts[k][1]);
        ctx.closePath();
        ctx.fillStyle = `rgb(${col[0]},${col[1]},${col[2]})`;
        ctx.fill();
        ctx.strokeStyle = `rgba(150,150,150,${0.10 * fog})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
    const out = canvas.getContext('2d');
    out.globalAlpha = o.alpha;
    out.drawImage(off, 0, 0);
  };
})();
