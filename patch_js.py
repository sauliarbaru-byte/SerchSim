import re

with open('main.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Add Garis Lintang to ALGO_INFO
algo_info_replacement = """  garislintang: { title: 'Garis Lintang', desc: 'Custom algorithm by Panji. Memprioritaskan jalur yang mendekati garis lurus antara start dan goal. f(n) = D_goal + k * T', type: 'informed' },
  bfs:"""
js = js.replace("bfs:", algo_info_replacement, 1)

# 2. Add 3D state variables
three_vars_replacement = """let scene3d, camera3d, renderer3d, cells3d = [], animFrame3d;
let camAngle = Math.PI / 4;
let camPitch = Math.PI / 6;
let camZoom = 1;
let camPanX = 0, camPanY = 0;
let isDragging3D = false;
let lastMouseX = 0, lastMouseY = 0;
"""
js = js.replace("let scene3d, camera3d, renderer3d, cells3d = [], animFrame3d;", three_vars_replacement)

# 3. Add to initAlgorithm
init_algo_replacement = """    case 'garislintang':
      algoState.pq = [{r:s.r,c:s.c,g:0,f:heuristic(s,g)}];
      algoState.gScore = {[key(s.r,s.c)]:0};
      break;
    case 'bfs':"""
js = js.replace("case 'bfs':", init_algo_replacement, 1)

# 4. Add to stepAlgorithm
step_algo_replacement = """    case 'garislintang': return stepGarisLintang(s,g,key);
    case 'bfs':"""
js = js.replace("case 'bfs':", step_algo_replacement, 1)

# 5. Add stepGarisLintang function
garis_lintang_func = """function stepGarisLintang(s,g,key) {
  const as = algoState;
  if (!as.pq.length) return noPath();
  as.pq.sort((a,b)=>a.f-b.f);
  const cur = as.pq.shift();
  const {r,c,g:gv} = cur;
  const k = key(r,c);
  if (as.visited.has(k)) return false;
  as.visited.add(k);
  markCurrent(r,c); markVisited(r,c);
  
  const h = Math.round(heuristic({r,c},g)*10)/10;
  consoleLog('step', `GarisLintang → (${r},${c}) f=${Math.round(cur.f*10)/10}`);
  if (r===g.r && c===g.c) return foundGoal(as.parent,key,r,c);
  
  getNeighbors(r,c).forEach(n => {
    const nk = key(n.r,n.c);
    const ng = gv+1;
    if (!as.gScore[nk] || ng < as.gScore[nk]) {
      as.gScore[nk]=ng; as.parent[nk]=key(r,c);
      
      // Calculate f = D_goal + k * T
      const k_val = 2.5; // penalti
      const d_goal = Math.sqrt(Math.pow(n.r-g.r, 2) + Math.pow(n.c-g.c, 2));
      const dx = g.c - s.c;
      const dy = g.r - s.r;
      let cross = 0;
      if (dx === 0 && dy === 0) {
        cross = Math.sqrt(Math.pow(n.r-s.r, 2) + Math.pow(n.c-s.c, 2));
      } else {
        cross = Math.abs(dx * (s.r - n.r) - (s.c - n.c) * dy) / Math.sqrt(dx*dx + dy*dy);
      }
      const f = d_goal + k_val * cross;
      
      as.pq.push({...n,g:ng,f:f});
      markQueued(n.r,n.c);
    }
  });
  updateQueueDisplay(as.pq);
  return false;
}

// ===================== ALGORITHMS ====================="""
js = js.replace("// ===================== ALGORITHMS =====================", garis_lintang_func, 1)

# 6. Replace init3D and render3D
render3d_replacement = """function init3D() {
  const canvas = document.getElementById('threeCanvas');
  const wrap = document.getElementById('grid3d');
  canvas.width = wrap.clientWidth;
  canvas.height = wrap.clientHeight;
  const ctx = canvas.getContext('2d');
  
  // Events
  canvas.onmousedown = (e) => {
    isDragging3D = true;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    canvas.classList.add('dragging');
  };
  window.onmousemove = (e) => {
    if (!isDragging3D || currentView !== '3d') return;
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    
    if (e.buttons === 1) {
        camAngle -= dx * 0.01;
        camPitch -= dy * 0.01;
        camPitch = Math.max(0, Math.min(Math.PI / 2 - 0.1, camPitch));
    } else if (e.buttons === 2) {
        camPanX += dx;
        camPanY += dy;
    }
    
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
  };
  window.onmouseup = () => {
    isDragging3D = false;
    canvas.classList.remove('dragging');
  };
  canvas.oncontextmenu = e => e.preventDefault();
  canvas.onwheel = (e) => {
    if (currentView !== '3d') return;
    e.preventDefault();
    camZoom *= (1 - e.deltaY * 0.001);
    camZoom = Math.max(0.2, Math.min(5, camZoom));
  };
  
  cancelAnimationFrame(animFrame3d);
  render3D(ctx, canvas.width, canvas.height);
}

function render3D(ctx, W, H) {
  ctx.clearRect(0, 0, W, H);
  
  const project = (c, r, h) => {
      const ox = (c - gridCols/2) * 20;
      const oy = (r - gridRows/2) * 20;
      const oz = h * 20;
      
      const rx = ox * Math.cos(camAngle) - oy * Math.sin(camAngle);
      const ry = ox * Math.sin(camAngle) + oy * Math.cos(camAngle);
      
      const fz = oz * Math.cos(camPitch) - ry * Math.sin(camPitch);
      const fy = ry * Math.cos(camPitch) + oz * Math.sin(camPitch);
      
      return {
          x: W/2 + camPanX + rx * camZoom,
          y: H/2 + camPanY - fy * camZoom,
          depth: fz + ry
      };
  };

  let renderList = [];
  for (let r = 0; r < gridRows; r++) {
    for (let c = 0; c < gridCols; c++) {
      const state = grid[r][c];
      const isWall = state === 'wall';
      const hLevel = isWall ? 1 : (state === 'current' ? 0.6 : state === 'visited' ? 0.3 : state === 'queued' ? 0.4 : state === 'path' ? 0.7 : state === 'start' || state === 'goal' ? 0.8 : 0.1);
      
      const p = project(c, r, 0);
      renderList.push({r, c, state, hLevel, depth: p.depth});
    }
  }
  
  renderList.sort((a, b) => b.depth - a.depth);

  renderList.forEach(cell => {
      const {r, c, state, hLevel} = cell;
      const col = get3DColor(state);
      
      const v = [];
      for(let dz of [0, hLevel]) {
          for(let dy of [-0.5, 0.5]) {
              for(let dx of [-0.5, 0.5]) {
                  v.push(project(c + dx, r + dy, dz));
              }
          }
      }
      
      ctx.beginPath();
      ctx.moveTo(v[4].x, v[4].y); ctx.lineTo(v[5].x, v[5].y);
      ctx.lineTo(v[7].x, v[7].y); ctx.lineTo(v[6].x, v[6].y);
      ctx.closePath();
      ctx.fillStyle = col; ctx.fill();
      ctx.strokeStyle = 'rgba(0,0,0,0.3)'; ctx.lineWidth = 0.5; ctx.stroke();
      
      if (hLevel > 0.1) {
          ctx.beginPath();
          ctx.moveTo(v[4].x, v[4].y); ctx.lineTo(v[6].x, v[6].y);
          ctx.lineTo(v[2].x, v[2].y); ctx.lineTo(v[0].x, v[0].y);
          ctx.closePath();
          ctx.fillStyle = shadeColor(col, -40); ctx.fill(); ctx.stroke();
          
          ctx.beginPath();
          ctx.moveTo(v[6].x, v[6].y); ctx.lineTo(v[7].x, v[7].y);
          ctx.lineTo(v[3].x, v[3].y); ctx.lineTo(v[2].x, v[2].y);
          ctx.closePath();
          ctx.fillStyle = shadeColor(col, -25); ctx.fill(); ctx.stroke();
      }
      
      if (state === 'start' || state === 'goal') {
        const topCenter = project(c, r, hLevel + 0.2);
        ctx.fillStyle = '#fff';
        ctx.font = 'bold 10px JetBrains Mono';
        ctx.textAlign = 'center';
        ctx.fillText(state === 'start' ? 'S' : 'G', topCenter.x, topCenter.y);
      }
  });

  animFrame3d = requestAnimationFrame(() => render3D(ctx, W, H));
}"""

# Need to find the old init3D and render3D and replace it
# They are between "// ===================== 3D VIEW =====================" and "function shadeColor"
import re
js = re.sub(r'function init3D\(\) \{.*?\}\s*function render3D\(ctx, W, H\) \{.*?\}', render3d_replacement, js, flags=re.DOTALL)

with open('main.js', 'w', encoding='utf-8') as f:
    f.write(js)
print('main.js patched successfully.')
