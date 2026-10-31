import os

html_content = r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
  <title>The Last Hour: Project Echo</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; -webkit-touch-callout: none; -webkit-user-select: none; user-select: none; }
    body, html { width: 100%; height: 100%; overflow: hidden; background: #000; font-family: 'Courier New', Courier, monospace; }
    #canvas3d { position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: block; z-index: 1; }

    /* CRT Post-processing overlay */
    #crt-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 5; pointer-events: none;
      background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.28) 50%),
                  radial-gradient(ellipse at center, rgba(0,0,0,0) 65%, rgba(0,0,0,0.65) 100%);
      background-size: 100% 3px, 100% 100%;
    }

    /* HUD Header - Authentic to Desktop */
    #hud-top-left {
      position: absolute; top: 16px; left: 20px; z-index: 10; pointer-events: none;
      text-shadow: 0 0 6px rgba(0, 240, 255, 0.4), 0 2px 4px rgba(0,0,0,0.9);
    }
    #hud-facility {
      font-size: 15px; font-weight: bold; color: #f0f2f5; letter-spacing: 1.5px;
    }
    #hud-sector {
      font-size: 12px; font-weight: bold; color: #49e8ff; letter-spacing: 1px; margin-top: 3px;
    }
    #hud-env {
      font-size: 11px; color: #a5afb9; letter-spacing: 0.8px; margin-top: 3px;
    }

    /* Mission Objective Card */
    #objective-card {
      margin-top: 10px; background: rgba(5, 18, 25, 0.88); border-left: 3px solid #49e8ff;
      border-top: 1px solid rgba(73, 232, 255, 0.3); border-right: 1px solid rgba(73, 232, 255, 0.2);
      border-bottom: 1px solid rgba(73, 232, 255, 0.2); padding: 8px 14px; border-radius: 0 4px 4px 0;
      max-width: 360px; box-shadow: 0 4px 14px rgba(0,0,0,0.7);
    }
    #objective-tag {
      font-size: 10px; font-weight: bold; color: #49e8ff; letter-spacing: 1.2px; text-transform: uppercase;
    }
    #objective-text {
      font-size: 12px; color: #e2f4ff; margin-top: 4px; line-height: 1.35; font-family: 'Courier New', monospace;
    }

    /* Top-Right Status */
    #hud-top-right {
      position: absolute; top: 16px; right: 20px; z-index: 10; pointer-events: none;
      font-size: 12px; font-weight: bold; color: #a5afb9; text-shadow: 0 2px 4px #000;
      letter-spacing: 1px; background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 3px;
      border: 1px solid rgba(255,255,255,0.15);
    }
    #hud-torch-state { color: #ffd249; font-weight: bold; }

    /* Crosshair & Interaction Tooltip */
    #reticle-wrap {
      position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
      z-index: 10; pointer-events: none; text-align: center;
    }
    #reticle-dot {
      width: 4px; height: 4px; background: rgba(245, 245, 245, 0.85);
      border-radius: 50%; margin: 0 auto; box-shadow: 0 0 4px rgba(255,255,255,0.8);
      transition: all 0.15s ease;
    }
    #reticle-dot.interactable {
      width: 8px; height: 8px; background: #49e8ff; border-radius: 50%;
      box-shadow: 0 0 10px #49e8ff, 0 0 20px #49e8ff;
    }
    #interact-prompt {
      margin-top: 12px; font-size: 11px; font-weight: bold; color: #49e8ff;
      background: rgba(4, 20, 26, 0.9); border: 1px solid #49e8ff;
      padding: 4px 10px; border-radius: 3px; letter-spacing: 1px;
      display: none; white-space: nowrap; box-shadow: 0 0 8px rgba(73, 232, 255, 0.4);
    }

    /* Mobile Controls: Sleek Tactical Glass Aesthetic */
    #controls-layer {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      z-index: 20; pointer-events: auto;
    }
    #joy-zone {
      position: absolute; bottom: 0; left: 0; width: 45%; height: 60%;
      pointer-events: auto; touch-action: none;
    }
    #joy-base {
      position: absolute; width: 124px; height: 124px; border-radius: 50%;
      background: radial-gradient(circle, rgba(16, 32, 42, 0.75) 0%, rgba(8, 16, 22, 0.85) 100%);
      border: 2px solid rgba(73, 232, 255, 0.35); box-shadow: 0 0 16px rgba(0, 0, 0, 0.8), inset 0 0 12px rgba(73,232,255,0.15);
      transform: translate(-50%, -50%); display: none; pointer-events: none;
    }
    #joy-stick {
      position: absolute; width: 54px; height: 54px; border-radius: 50%;
      background: radial-gradient(circle, #49e8ff 0%, #15728a 100%);
      border: 2px solid #a8f4ff; box-shadow: 0 0 12px rgba(73, 232, 255, 0.6);
      transform: translate(-50%, -50%); top: 50%; left: 50%; pointer-events: none;
    }

    /* Action Buttons (Right Side) */
    .btn-action {
      position: absolute; border-radius: 50%; display: flex; align-items: center;
      justify-content: center; font-weight: bold; font-family: 'Courier New', monospace;
      user-select: none; touch-action: none; cursor: pointer; transition: transform 0.08s ease, box-shadow 0.15s ease;
      letter-spacing: 1px;
    }
    .btn-action:active { transform: scale(0.92); }

    #btn-use {
      bottom: 42px; right: 42px; width: 78px; height: 78px;
      background: radial-gradient(circle, rgba(20, 36, 46, 0.9) 0%, rgba(8, 18, 24, 0.95) 100%);
      border: 2px solid rgba(73, 232, 255, 0.5); color: #e2f8ff; font-size: 14px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.8);
    }
    #btn-use.ready {
      border-color: #49e8ff; color: #49e8ff;
      box-shadow: 0 0 18px rgba(73, 232, 255, 0.7), inset 0 0 14px rgba(73, 232, 255, 0.3);
      animation: pulse-use 1.4s infinite;
    }
    @keyframes pulse-use {
      0%, 100% { box-shadow: 0 0 12px rgba(73,232,255,0.5); }
      50% { box-shadow: 0 0 24px rgba(73,232,255,0.9), inset 0 0 16px rgba(73,232,255,0.4); }
    }

    #btn-torch {
      bottom: 136px; right: 46px; width: 62px; height: 62px;
      background: radial-gradient(circle, rgba(34, 30, 16, 0.9) 0%, rgba(18, 16, 10, 0.95) 100%);
      border: 2px solid rgba(255, 210, 73, 0.5); color: #ffd249; font-size: 11px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.7);
    }
    #btn-torch.active {
      background: radial-gradient(circle, rgba(65, 55, 20, 0.95) 0%, rgba(26, 22, 10, 0.95) 100%);
      border-color: #ffd249; box-shadow: 0 0 16px rgba(255, 210, 73, 0.7);
    }

    #btn-sprint {
      bottom: 50px; right: 134px; width: 56px; height: 56px;
      background: radial-gradient(circle, rgba(20, 26, 32, 0.9) 0%, rgba(10, 14, 18, 0.95) 100%);
      border: 2px solid rgba(165, 175, 185, 0.4); color: #c0ccd8; font-size: 11px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.7);
    }
    #btn-sprint.active {
      border-color: #49e8ff; color: #49e8ff; box-shadow: 0 0 12px rgba(73,232,255,0.5);
    }

    /* Modal Screens: Interactive Wire Puzzle & CRT Terminal */
    .modal-overlay {
      position: absolute; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(0, 0, 0, 0.88); z-index: 100; display: none;
      align-items: center; justify-content: center; backdrop-filter: blur(4px);
    }
    .modal-box {
      background: #060e13; border: 2px solid #49e8ff; border-radius: 6px;
      box-shadow: 0 0 30px rgba(73, 232, 255, 0.3), inset 0 0 20px rgba(0,0,0,0.9);
      padding: 18px; color: #49e8ff; max-width: 90%; max-height: 90%; overflow: auto;
      font-family: 'Courier New', monospace; position: relative;
    }
    .modal-close {
      position: absolute; top: 10px; right: 14px; font-size: 20px; font-weight: bold;
      color: #ff5555; cursor: pointer; padding: 4px 8px; border: 1px solid #ff5555; border-radius: 3px;
    }
    #wire-canvas {
      display: block; background: #0c141a; border: 1px solid rgba(73,232,255,0.4);
      margin: 12px auto; touch-action: none; border-radius: 4px;
    }
    .term-btn {
      background: rgba(73, 232, 255, 0.15); border: 1px solid #49e8ff; color: #49e8ff;
      padding: 8px 14px; font-family: 'Courier New', monospace; font-size: 13px; font-weight: bold;
      cursor: pointer; margin-top: 10px; border-radius: 3px;
    }
    .term-btn:active { background: #49e8ff; color: #000; }
  </style>
</head>
<body>
  <div id="crt-overlay"></div>

  <!-- Authentic Desktop HUD -->
  <div id="hud-top-left">
    <div id="hud-facility">ABANDONED FACILITY // MAIN LABORATORY</div>
    <div id="hud-sector">SECTOR STATUS: PRIMARY RESEARCH &amp; CONTROL</div>
    <div id="hud-env">ENVIRONMENT: GRID POWER OFFLINE  //  EVIDENCE AVAILABLE: 3</div>
    <div id="objective-card">
      <div id="objective-tag">[!] PRIORITY DIRECTIVE // ACT 1</div>
      <div id="objective-text">Main power grid offline! Locate auxiliary generator in the Engineering sector to repair conduit wiring.</div>
    </div>
  </div>

  <div id="hud-top-right">
    TORCH: <span id="hud-torch-state">[ON]</span> | <span id="hud-fps">60 FPS</span>
  </div>

  <div id="reticle-wrap">
    <div id="reticle-dot"></div>
    <div id="interact-prompt">[USE] EXAMINE</div>
  </div>

  <!-- Fullscreen Touch Interface -->
  <div id="controls-layer">
    <div id="joy-zone"></div>
    <div id="joy-base"><div id="joy-stick"></div></div>
    <div id="btn-use" class="btn-action">USE</div>
    <div id="btn-torch" class="btn-action active">LIGHT</div>
    <div id="btn-sprint" class="btn-action">RUN</div>
  </div>

  <!-- Interactive Modal: Auxiliary Generator Wire Repair -->
  <div id="wire-modal" class="modal-overlay">
    <div class="modal-box" style="width: 520px; text-align: center;">
      <div class="modal-close" id="btn-close-wire">&times;</div>
      <h3 style="letter-spacing: 2px; color: #ffd249;">AUXILIARY GENERATOR // RELAY BUS</h3>
      <p style="font-size: 11px; color: #8fa0b0; margin-top: 4px;">Connect matching circuit terminals to bypass blown fuses.</p>
      <canvas id="wire-canvas" width="460" height="240"></canvas>
      <div id="wire-status" style="font-size: 13px; font-weight: bold; color: #ffd249; margin-top: 6px;">DRAG WIRES TO MATCH TERMINALS (0/4 CONNECTED)</div>
    </div>
  </div>

  <!-- Interactive Modal: Welcome CRT Terminal -->
  <div id="term-modal" class="modal-overlay">
    <div class="modal-box" style="width: 600px; max-width: 92%;">
      <div class="modal-close" id="btn-close-term">&times;</div>
      <h3 style="letter-spacing: 2px; color: #49e8ff; border-bottom: 1px solid #49e8ff; padding-bottom: 6px;">PROJECT ECHO // WORKSTATION TERMINAL</h3>
      <div id="term-text" style="font-size: 12px; color: #9fe7b4; line-height: 1.5; margin-top: 10px; max-height: 260px; overflow-y: auto;">
        [AUTHENTICATED ACCESS: DR. ARIS THORNE]<br>
        -----------------------------------------------------<br>
        FACILITY SYSTEM REPORT // ANOMALOUS CORE MONITORING<br>
        The containment stasis field in the biological sector experienced severe harmonic decoupling at 02:41 AM.<br><br>
        WARNING: Manual circuit override required at auxiliary generator.<br>
        Once power is restored, authorize emergency door interlocks below.<br>
        -----------------------------------------------------
      </div>
      <div style="margin-top: 14px; text-align: right;">
        <button id="btn-term-override" class="term-btn">AUTHORIZE EMERGENCY OVERRIDE</button>
      </div>
    </div>
  </div>

  <canvas id="canvas3d"></canvas>

  <script src="three.min.js"></script>
  <script>
    // =========================================================================
    // THE LAST HOUR: PROJECT ECHO - MOBILE HIGH-FIDELITY ENGINE
    // Matches 100% of Desktop Room Architecture, PBR Textures, Stasis Chamber,
    // Server Bank, Wiring Puzzles, CRT Terminals, and Sound Effects.
    // =========================================================================

    // 1. PROCEDURAL PBR TEXTURE GENERATION (100% Offline, Zero Downloads)
    function makeConcreteFloorTexture() {
      const c = document.createElement('canvas'); c.width = 1024; c.height = 1024;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#22282d'; ctx.fillRect(0, 0, 1024, 1024);
      // Large floor tile grid (4x4 tiles per 1024)
      const tileSize = 256;
      for (let x = 0; x < 1024; x += tileSize) {
        for (let y = 0; y < 1024; y += tileSize) {
          const shade = 32 + Math.floor(Math.random() * 12);
          ctx.fillStyle = `rgb(${shade}, ${shade + 5}, ${shade + 8})`;
          ctx.fillRect(x + 2, y + 2, tileSize - 4, tileSize - 4);
          // Concrete noise & aggregate specks
          for (let i = 0; i < 400; i++) {
            const nx = x + Math.random() * tileSize, ny = y + Math.random() * tileSize;
            const b = Math.random() > 0.5 ? 60 : 15;
            ctx.fillStyle = `rgba(${b}, ${b}, ${b}, 0.25)`;
            ctx.fillRect(nx, ny, 2 + Math.random() * 3, 2 + Math.random() * 3);
          }
          // Wear scratches and stains
          ctx.strokeStyle = 'rgba(10, 15, 18, 0.4)'; ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(x + Math.random() * tileSize, y + Math.random() * tileSize);
          ctx.lineTo(x + Math.random() * tileSize, y + Math.random() * tileSize);
          ctx.stroke();
        }
      }
      // Tile grout seam borders
      ctx.strokeStyle = '#0d1216'; ctx.lineWidth = 4;
      for (let p = 0; p <= 1024; p += tileSize) {
        ctx.beginPath(); ctx.moveTo(p, 0); ctx.lineTo(p, 1024); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, p); ctx.lineTo(1024, p); ctx.stroke();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(8, 8);
      return tex;
    }

    function makeBunkerWallTexture() {
      const c = document.createElement('canvas'); c.width = 1024; c.height = 1024;
      const ctx = c.getContext('2d');
      // Dark reinforced bunker steel-concrete base
      ctx.fillStyle = '#1c242a'; ctx.fillRect(0, 0, 1024, 1024);
      // Horizontal reinforced wall panels (4 panels)
      for (let i = 0; i < 4; i++) {
        const y = i * 256;
        const grad = ctx.createLinearGradient(0, y, 0, y + 256);
        grad.addColorStop(0, '#27323b'); grad.addColorStop(0.5, '#1e262e'); grad.addColorStop(1, '#151c22');
        ctx.fillStyle = grad; ctx.fillRect(4, y + 4, 1016, 248);
        // Rivets along panel seam lines
        ctx.fillStyle = '#3a4a56';
        for (let rx = 32; rx < 1024; rx += 64) {
          ctx.beginPath(); ctx.arc(rx, y + 16, 4, 0, Math.PI * 2); ctx.fill();
          ctx.beginPath(); ctx.arc(rx, y + 240, 4, 0, Math.PI * 2); ctx.fill();
        }
        // Rust streaks running down
        for (let r = 0; r < 3; r++) {
          const rx = 100 + Math.random() * 800;
          ctx.fillStyle = 'rgba(75, 45, 20, 0.28)';
          ctx.fillRect(rx, y + 20, 10 + Math.random() * 20, 120 + Math.random() * 100);
        }
      }
      // Industrial stencil stamp
      ctx.fillStyle = 'rgba(73, 232, 255, 0.4)'; ctx.font = 'bold 24px Courier New';
      ctx.fillText('SECTOR-04 // LAB-B // PROJECT ECHO', 60, 180);
      ctx.fillText('RESTRICTED ACCESS ONLY', 60, 436);
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(4, 1);
      return tex;
    }

    function makeHazardTexture() {
      const c = document.createElement('canvas'); c.width = 256; c.height = 64;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#ffd249'; ctx.fillRect(0, 0, 256, 64);
      ctx.fillStyle = '#111';
      for (let x = -64; x < 320; x += 32) {
        ctx.beginPath();
        ctx.moveTo(x, 0); ctx.lineTo(x + 16, 0); ctx.lineTo(x - 8, 64); ctx.lineTo(x - 24, 64);
        ctx.closePath(); ctx.fill();
      }
      const tex = new THREE.CanvasTexture(c);
      tex.wrapS = THREE.RepeatWrapping; tex.wrapT = THREE.RepeatWrapping;
      tex.repeat.set(4, 1);
      return tex;
    }

    function makeCRTTexture() {
      const c = document.createElement('canvas'); c.width = 512; c.height = 384;
      const ctx = c.getContext('2d');
      ctx.fillStyle = '#06130b'; ctx.fillRect(0, 0, 512, 384);
      // Phosphor scanline bars
      ctx.fillStyle = 'rgba(30, 240, 120, 0.08)';
      for (let y = 0; y < 384; y += 4) ctx.fillRect(0, y, 512, 2);
      // Terminal Header
      ctx.fillStyle = '#20ff78'; ctx.font = 'bold 18px Courier New';
      ctx.fillText('PROJECT ECHO // TERMINAL v1.87', 24, 38);
      ctx.fillStyle = '#10c058'; ctx.font = '13px Courier New';
      ctx.fillText('STATUS: EMERGENCY PROTOCOL ACTIVE', 24, 68);
      ctx.fillText('GRID: [OFFLINE] - AUXILIARY ENGAGED', 24, 92);
      ctx.fillText('CONTAINMENT CHAMBER: STABILIZED', 24, 116);
      ctx.fillText('SECURITY BREACH: SECTOR 4 LOCKDOWN', 24, 140);
      ctx.fillStyle = '#20ff78';
      ctx.fillText('> PRESS [USE] TO OPERATE TERMINAL', 24, 190);
      const tex = new THREE.CanvasTexture(c);
      return { canvas: c, ctx: ctx, texture: tex };
    }

    // 2. PROCEDURAL WEB AUDIO SYNTHESIZER (100% Offline, Zero Asset Downloads)
    let audioCtx = null;
    function initAudio() {
      if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      if (audioCtx.state === 'suspended') audioCtx.resume();
    }
    function playHum() {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
      osc.type = 'sawtooth'; osc.frequency.setValueAtTime(55, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.start();
    }
    function playBeep(freq = 880, dur = 0.08) {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
      osc.type = 'sine'; osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.12, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + dur);
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.start(); osc.stop(audioCtx.currentTime + dur);
    }
    function playSpark() {
      if (!audioCtx) return;
      const osc = audioCtx.createOscillator(); const gain = audioCtx.createGain();
      osc.type = 'square';
      osc.frequency.setValueAtTime(200 + Math.random() * 800, audioCtx.currentTime);
      gain.gain.setValueAtTime(0.18, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.12);
      osc.connect(gain); gain.connect(audioCtx.destination);
      osc.start(); osc.stop(audioCtx.currentTime + 0.12);
    }
    function playStep() {
      if (!audioCtx) return;
      const buf = audioCtx.createBuffer(1, audioCtx.sampleRate * 0.06, audioCtx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < data.length; i++) data[i] = (Math.random() * 2 - 1) * Math.exp(-i / (data.length * 0.25));
      const src = audioCtx.createBufferSource(); const gain = audioCtx.createGain();
      src.buffer = buf; gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
      src.connect(gain); gain.connect(audioCtx.destination);
      src.start();
    }

    // 3. THREE.JS SCENE SETUP
    const canvas = document.getElementById('canvas3d');
    const renderer = new THREE.WebGLRenderer({ canvas: canvas, antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x060c10);
    scene.fog = new THREE.FogExp2(0x060c10, 0.045);

    const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 100);
    camera.position.set(0, 1.65, 0);

    // Lighting Systems
    const ambientLight = new THREE.AmbientLight(0x0c161f, 0.7);
    scene.add(ambientLight);

    // Player Flashlight (SpotLight)
    const torch = new THREE.SpotLight(0xfff5dd, 2.8, 22, Math.PI / 5.5, 0.45, 1.4);
    torch.position.set(0, 1.65, 0);
    torch.castShadow = true;
    torch.shadow.mapSize.width = 1024; torch.shadow.mapSize.height = 1024;
    scene.add(torch); scene.add(torch.target);

    // Facility Emergency Overhead Light
    const mainLight = new THREE.PointLight(0x8fe2ff, 0.0, 30);
    mainLight.position.set(0, 4.0, 0);
    scene.add(mainLight);

    // 4. LABORATORY 3D ARCHITECTURE & PROPS
    const floorTex = makeConcreteFloorTexture();
    const wallTex = makeBunkerWallTexture();
    const hazardTex = makeHazardTexture();
    const crtData = makeCRTTexture();

    const floorMat = new THREE.MeshStandardMaterial({ map: floorTex, roughness: 0.65, metalness: 0.25 });
    const wallMat = new THREE.MeshStandardMaterial({ map: wallTex, roughness: 0.7, metalness: 0.4 });
    const ceilingMat = new THREE.MeshStandardMaterial({ color: 0x11171d, roughness: 0.85 });

    // Main Room Dimensions: 36m x 36m x 4.5m
    const roomW = 36, roomL = 36, roomH = 4.5;
    const halfW = roomW / 2, halfL = roomL / 2;

    // Floor & Ceiling
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(roomW, roomL), floorMat);
    floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);

    const ceiling = new THREE.Mesh(new THREE.PlaneGeometry(roomW, roomL), ceilingMat);
    ceiling.position.y = roomH; ceiling.rotation.x = Math.PI / 2; scene.add(ceiling);

    // Industrial Overhead Girders
    const girderMat = new THREE.MeshStandardMaterial({ color: 0x182026, metalness: 0.8, roughness: 0.3 });
    for (let gz = -12; gz <= 12; gz += 8) {
      const girder = new THREE.Mesh(new THREE.BoxGeometry(roomW, 0.35, 0.35), girderMat);
      girder.position.set(0, roomH - 0.18, gz); scene.add(girder);
    }

    // Walls
    function makeWall(w, h, x, y, z, rotY) {
      const m = new THREE.Mesh(new THREE.PlaneGeometry(w, h), wallMat);
      m.position.set(x, y, z); m.rotation.y = rotY; m.receiveShadow = true;
      scene.add(m);
    }
    makeWall(roomW, roomH, 0, roomH / 2, -halfL, 0); // North
    makeWall(roomW, roomH, 0, roomH / 2, halfL, Math.PI); // South
    makeWall(roomL, roomH, -halfW, roomH / 2, 0, Math.PI / 2); // West
    makeWall(roomL, roomH, halfW, roomH / 2, 0, -Math.PI / 2); // East

    // Ceiling Lighting Fixtures
    const fixtureMat = new THREE.MeshStandardMaterial({ color: 0x1c242b, metalness: 0.75 });
    const tubeMat = new THREE.MeshBasicMaterial({ color: 0x66ccee });
    const fixtures = [];
    for (let fx of [-8, 8]) {
      for (let fz of [-8, 8]) {
        const fix = new THREE.Mesh(new THREE.BoxGeometry(1.2, 0.12, 3.2), fixtureMat);
        fix.position.set(fx, roomH - 0.08, fz); scene.add(fix);
        const tube = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 3.0, 8), tubeMat);
        tube.position.set(fx, roomH - 0.18, fz); tube.rotation.x = Math.PI / 2; scene.add(tube);
        fixtures.push(tube);
      }
    }

    // Ceiling Industrial Pipes
    const pipeMat = new THREE.MeshStandardMaterial({ color: 0x2b3842, metalness: 0.85, roughness: 0.25 });
    for (let px of [-14, -6, 6, 14]) {
      const pipe = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.08, roomL, 8), pipeMat);
      pipe.position.set(px, roomH - 0.35, 0); pipe.rotation.x = Math.PI / 2; scene.add(pipe);
    }

    // Interactive Objects Registry for Raycasting
    const interactables = [];

    // --- PROP 1: THE BIOLOGICAL STASIS CHAMBER (West Wing) ---
    const stasisGroup = new THREE.Group();
    stasisGroup.position.set(-14.0, 0, -6.0);
    const metalDarkMat = new THREE.MeshStandardMaterial({ color: 0x1a2228, roughness: 0.35, metalness: 0.85 });
    const baseCyl = new THREE.Mesh(new THREE.CylinderGeometry(1.5, 1.6, 0.45, 24), metalDarkMat);
    baseCyl.position.y = 0.22; stasisGroup.add(baseCyl);
    const topCyl = new THREE.Mesh(new THREE.CylinderGeometry(1.6, 1.5, 0.4, 24), metalDarkMat);
    topCyl.position.y = 3.8; stasisGroup.add(topCyl);
    // Outer Glass
    const glassMat = new THREE.MeshStandardMaterial({ color: 0x33aa88, roughness: 0.08, metalness: 0.1, transparent: true, opacity: 0.38 });
    const glassCyl = new THREE.Mesh(new THREE.CylinderGeometry(1.28, 1.28, 3.2, 24), glassMat);
    glassCyl.position.y = 2.0; stasisGroup.add(glassCyl);
    // Inner Bioluminescent Fluid
    const fluidMat = new THREE.MeshStandardMaterial({ color: 0x1fe67c, emissive: 0x0fa855, emissiveIntensity: 0.6, roughness: 0.2, transparent: true, opacity: 0.72 });
    const fluidCyl = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.15, 2.9, 24), fluidMat);
    fluidCyl.position.y = 1.9; stasisGroup.add(fluidCyl);
    // Green Point Light inside chamber
    const stasisLight = new THREE.PointLight(0x1fe67c, 1.6, 14);
    stasisLight.position.set(-14.0, 2.0, -6.0); scene.add(stasisLight);
    scene.add(stasisGroup);

    // --- PROP 2: PHASE 1 SERVER BANK (North Wall) ---
    const serverMat = new THREE.MeshStandardMaterial({ color: 0x12171c, metalness: 0.85, roughness: 0.35 });
    for (let rx of [-13, -10.5, 10.5, 13]) {
      const rack = new THREE.Mesh(new THREE.BoxGeometry(2.0, 3.8, 1.1), serverMat);
      rack.position.set(rx, 1.9, -halfL + 0.6); rack.castShadow = true; scene.add(rack);
      // Blinking status LEDs on each server rack
      for (let ly = 0.8; ly <= 3.2; ly += 0.45) {
        const ledMat = new THREE.MeshBasicMaterial({ color: Math.random() > 0.3 ? 0x20ff60 : 0xffaa20 });
        const led = new THREE.Mesh(new THREE.BoxGeometry(0.04, 0.04, 0.04), ledMat);
        led.position.set(rx + 0.7, ly, -halfL + 1.16); scene.add(led);
      }
    }

    // --- PROP 3: MAIN WORKSTATION & CRT TERMINAL (Center) ---
    const deskMat = new THREE.MeshStandardMaterial({ color: 0x222a30, roughness: 0.65, metalness: 0.3 });
    const desk = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.9, 1.8), deskMat);
    desk.position.set(-2.5, 0.45, -2.0); desk.castShadow = true; scene.add(desk);
    // CRT Body & Screen
    const crtCasingMat = new THREE.MeshStandardMaterial({ color: 0x181f25, roughness: 0.5 });
    const crtBody = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.8, 0.75), crtCasingMat);
    crtBody.position.set(-2.5, 1.35, -2.1); crtBody.castShadow = true; scene.add(crtBody);
    const crtScreenMat = new THREE.MeshBasicMaterial({ map: crtData.texture });
    const crtScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.82, 0.62), crtScreenMat);
    crtScreen.position.set(-2.5, 1.35, -1.72); scene.add(crtScreen);
    // Green Terminal Glow Light
    const crtGlow = new THREE.PointLight(0x20ff78, 0.8, 5);
    crtGlow.position.set(-2.5, 1.35, -1.4); scene.add(crtGlow);
    // Keyboard & Case Folder
    const kb = new THREE.Mesh(new THREE.BoxGeometry(0.8, 0.04, 0.3), new THREE.MeshStandardMaterial({ color: 0x141a1f }));
    kb.position.set(-2.5, 0.92, -1.5); scene.add(kb);
    // Lab Oscilloscope on desk
    const oscBody = new THREE.Mesh(new THREE.BoxGeometry(0.85, 0.55, 0.6), new THREE.MeshStandardMaterial({ color: 0x28343e }));
    oscBody.position.set(-3.7, 1.2, -2.0); scene.add(oscBody);
    const oscScreen = new THREE.Mesh(new THREE.PlaneGeometry(0.4, 0.35), new THREE.MeshBasicMaterial({ color: 0x0fa855 }));
    oscScreen.position.set(-3.7, 1.2, -1.69); scene.add(oscScreen);

    // Register Terminal as Interactable
    crtBody.userData = { type: 'terminal', name: 'PROJECT ECHO TERMINAL' };
    interactables.push(crtBody);

    // --- PROP 4: AUXILIARY GENERATOR & WIRE REPAIR UNIT (East Wing) ---
    const genBodyMat = new THREE.MeshStandardMaterial({ color: 0x28343e, metalness: 0.8, roughness: 0.3 });
    const generator = new THREE.Mesh(new THREE.BoxGeometry(2.8, 2.5, 2.2), genBodyMat);
    generator.position.set(12.0, 1.25, -8.0); generator.castShadow = true; scene.add(generator);
    const genBorder = new THREE.Mesh(new THREE.PlaneGeometry(2.8, 0.22), new THREE.MeshBasicMaterial({ map: hazardTex }));
    genBorder.position.set(12.0, 2.4, -6.89); scene.add(genBorder);
    const genDoor = new THREE.Mesh(new THREE.BoxGeometry(1.3, 1.4, 0.08), new THREE.MeshStandardMaterial({ color: 0x485866, metalness: 0.7 }));
    genDoor.position.set(12.0, 1.25, -6.88); scene.add(genDoor);
    // Exhaust pipe running up to ceiling
    const exhaust = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, roomH - 2.5, 12), pipeMat);
    exhaust.position.set(12.9, 3.4, -8.0); scene.add(exhaust);

    generator.userData = { type: 'generator', name: 'AUXILIARY GENERATOR' };
    interactables.push(generator);

    // --- PROP 5: EMERGENCY BREAKER KNIFE SWITCH (South Wall) ---
    const switchBox = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.6, 0.12), new THREE.MeshStandardMaterial({ color: 0x445566, metalness: 0.7 }));
    switchBox.position.set(-8.0, 1.6, halfL - 0.06); scene.add(switchBox);
    const switchLever = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.22, 0.14), new THREE.MeshStandardMaterial({ color: 0xee2222, roughness: 0.4 }));
    switchLever.position.set(-8.0, 1.6, halfL - 0.12); scene.add(switchLever);
    switchBox.userData = { type: 'switch', name: 'EMERGENCY BREAKER SWITCH' };
    interactables.push(switchBox);

    // --- PROP 6: SECURITY SURVEILLANCE CAMERA (Blinking LED) ---
    const camMat = new THREE.MeshStandardMaterial({ color: 0x111, metalness: 0.8 });
    const camBody = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.14, 0.4, 8), camMat);
    camBody.position.set(halfW - 0.6, roomH - 0.5, halfL - 0.6);
    camBody.rotation.x = 0.5; camBody.rotation.y = -0.5; scene.add(camBody);
    const camLed = new THREE.PointLight(0xff2222, 0.8, 4);
    camLed.position.set(halfW - 0.8, roomH - 0.6, halfL - 0.8); scene.add(camLed);

    // --- PROP 7: ATMOSPHERIC DUST PARTICLES ---
    const dustGeo = new THREE.BufferGeometry();
    const dustCount = 280;
    const dustPos = new Float32Array(dustCount * 3);
    for (let i = 0; i < dustCount * 3; i += 3) {
      dustPos[i] = (Math.random() - 0.5) * roomW;
      dustPos[i + 1] = Math.random() * roomH;
      dustPos[i + 2] = (Math.random() - 0.5) * roomL;
    }
    dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
    const dustMat = new THREE.PointsMaterial({ color: 0xaaccff, size: 0.04, transparent: true, opacity: 0.45 });
    const dustParticles = new THREE.Points(dustGeo, dustMat);
    scene.add(dustParticles);

    // 5. GAME STATE & STORY PROGRESSION
    let powerRestored = false;
    let overrideAuthorized = false;
    let torchActive = true;
    let isSprinting = false;

    // 6. RAYCASTING INTERACTION SYSTEM
    const raycaster = new THREE.Raycaster();
    const centerVec = new THREE.Vector2(0, 0);
    let activeInteractable = null;

    const reticleDot = document.getElementById('reticle-dot');
    const interactPrompt = document.getElementById('interact-prompt');
    const btnUse = document.getElementById('btn-use');

    function checkRaycast() {
      raycaster.setFromCamera(centerVec, camera);
      const hits = raycaster.intersectObjects(interactables, false);
      if (hits.length > 0 && hits[0].distance < 4.2) {
        activeInteractable = hits[0].object.userData;
        reticleDot.classList.add('interactable');
        interactPrompt.style.display = 'block';
        interactPrompt.innerText = `[USE] ${activeInteractable.name}`;
        btnUse.classList.add('ready');
      } else {
        activeInteractable = null;
        reticleDot.classList.remove('interactable');
        interactPrompt.style.display = 'none';
        btnUse.classList.remove('ready');
      }
    }

    function executeInteraction() {
      initAudio();
      if (!activeInteractable) return;
      playBeep(720, 0.06);

      if (activeInteractable.type === 'terminal') {
        openTerminalModal();
      } else if (activeInteractable.type === 'generator') {
        if (!powerRestored) {
          openWireModal();
        } else {
          document.getElementById('objective-text').innerText = 'Power already stabilized! Proceed to the Welcome Terminal to authorize facility override.';
        }
      } else if (activeInteractable.type === 'switch') {
        playSpark();
        if (powerRestored) {
          mainLight.intensity = (mainLight.intensity > 0.5) ? 0.0 : 1.4;
          playBeep(440, 0.1);
        } else {
          document.getElementById('objective-text').innerText = 'Circuit breaker tripped! Restore auxiliary generator wiring first.';
        }
      }
    }

    // 7. INTERACTIVE MODAL SYSTEMS: WIRE PUZZLE & TERMINAL
    const wireModal = document.getElementById('wire-modal');
    const wireCanvas = document.getElementById('wire-canvas');
    const wireCtx = wireCanvas.getContext('2d');
    const wireStatus = document.getElementById('wire-status');

    const terminals = [
      { id: 0, color: '#ff3344', name: 'RED', y: 40, connected: false },
      { id: 1, color: '#3388ff', name: 'BLUE', y: 90, connected: false },
      { id: 2, color: '#ffd249', name: 'YELLOW', y: 140, connected: false },
      { id: 3, color: '#20ff78', name: 'GREEN', y: 190, connected: false }
    ];
    let selectedTerminal = null;

    function renderWirePuzzle() {
      wireCtx.fillStyle = '#0b1419'; wireCtx.fillRect(0, 0, wireCanvas.width, wireCanvas.height);
      // Grid lines
      wireCtx.strokeStyle = 'rgba(73, 232, 255, 0.08)'; wireCtx.lineWidth = 1;
      for (let x = 0; x < wireCanvas.width; x += 20) { wireCtx.beginPath(); wireCtx.moveTo(x, 0); wireCtx.lineTo(x, 240); wireCtx.stroke(); }
      for (let y = 0; y < wireCanvas.height; y += 20) { wireCtx.beginPath(); wireCtx.moveTo(0, y); wireCtx.lineTo(460, y); wireCtx.stroke(); }

      // Draw terminals on Left (inputs) and Right (relays)
      terminals.forEach((t) => {
        // Left Pin
        wireCtx.fillStyle = t.color;
        wireCtx.beginPath(); wireCtx.arc(50, t.y, 14, 0, Math.PI * 2); wireCtx.fill();
        wireCtx.strokeStyle = '#fff'; wireCtx.lineWidth = 2; wireCtx.stroke();
        // Right Pin
        wireCtx.fillStyle = t.color;
        wireCtx.beginPath(); wireCtx.arc(410, t.y, 14, 0, Math.PI * 2); wireCtx.fill();
        wireCtx.stroke();

        // Connected Wires
        if (t.connected) {
          wireCtx.strokeStyle = t.color; wireCtx.lineWidth = 6; wireCtx.shadowColor = t.color; wireCtx.shadowBlur = 12;
          wireCtx.beginPath(); wireCtx.moveTo(50, t.y);
          wireCtx.bezierCurveTo(180, t.y, 280, t.y, 410, t.y);
          wireCtx.stroke();
          wireCtx.shadowBlur = 0;
        }
      });
    }

    function openWireModal() { wireModal.style.display = 'flex'; renderWirePuzzle(); }
    document.getElementById('btn-close-wire').onclick = () => { wireModal.style.display = 'none'; };

    wireCanvas.addEventListener('pointerdown', (e) => {
      const rect = wireCanvas.getBoundingClientRect();
      const px = e.clientX - rect.left, py = e.clientY - rect.top;
      terminals.forEach(t => {
        if (Math.hypot(px - 50, py - t.y) < 26) {
          selectedTerminal = t;
          playBeep(520, 0.05);
        }
      });
    });

    wireCanvas.addEventListener('pointerup', (e) => {
      if (!selectedTerminal) return;
      const rect = wireCanvas.getBoundingClientRect();
      const px = e.clientX - rect.left, py = e.clientY - rect.top;
      terminals.forEach(t => {
        if (t.id === selectedTerminal.id && Math.hypot(px - 410, py - t.y) < 32) {
          t.connected = true;
          playSpark(); playBeep(880, 0.1);
        }
      });
      selectedTerminal = null;
      renderWirePuzzle();

      const doneCount = terminals.filter(t => t.connected).length;
      wireStatus.innerText = `CIRCUITS CONNECTED: (${doneCount}/4)`;
      if (doneCount === 4) {
        powerRestored = true;
        wireStatus.innerText = 'POWER SURGE DETECTED! AUXILIARY GRID ONLINE!';
        playSpark(); playHum();
        mainLight.intensity = 1.35;
        document.getElementById('hud-env').innerText = 'ENVIRONMENT: GRID POWER RESTORED  //  EVIDENCE AVAILABLE: 3';
        document.getElementById('objective-text').innerText = 'Power restored! Access the Welcome Terminal at the central desk to authorize facility security override.';
        setTimeout(() => { wireModal.style.display = 'none'; }, 1200);
      }
    });

    // Terminal Modal
    const termModal = document.getElementById('term-modal');
    function openTerminalModal() { termModal.style.display = 'flex'; }
    document.getElementById('btn-close-term').onclick = () => { termModal.style.display = 'none'; };
    document.getElementById('btn-term-override').onclick = () => {
      if (!powerRestored) {
        alert('ERROR: MAIN POWER GRID OFFLINE. Cannot authorize override.');
        return;
      }
      playBeep(980, 0.15);
      overrideAuthorized = true;
      document.getElementById('objective-tag').innerText = '[!] DIRECTIVE COMPLETE // ESCAPE PROTOCOL';
      document.getElementById('objective-text').innerText = 'OVERRIDE COMPLETE! Sector 4 blast doors unlocked. Evacuate to the Observation Wing!';
      termModal.style.display = 'none';
    };

    // 8. MOBILE DUAL TOUCH CONTROLLER (Joystick + Look Swipe + Buttons)
    const joyZone = document.getElementById('joy-zone');
    const joyBase = document.getElementById('joy-base');
    const joyStick = document.getElementById('joy-stick');
    let joyActive = false, joyOrigin = { x: 0, y: 0 }, joyVec = { x: 0, y: 0 };
    let joyTouchId = null, lookTouchId = null;
    let lookLast = { x: 0, y: 0 };
    let camYaw = 0, camPitch = 0;

    joyZone.addEventListener('touchstart', (e) => {
      initAudio();
      for (let t of e.changedTouches) {
        if (joyTouchId === null) {
          joyTouchId = t.identifier;
          joyActive = true;
          joyOrigin = { x: t.clientX, y: t.clientY };
          joyBase.style.left = `${t.clientX}px`; joyBase.style.top = `${t.clientY}px`;
          joyBase.style.display = 'block';
          joyStick.style.left = '50%'; joyStick.style.top = '50%';
          joyVec = { x: 0, y: 0 };
          break;
        }
      }
    }, { passive: false });

    window.addEventListener('touchmove', (e) => {
      for (let t of e.changedTouches) {
        if (t.identifier === joyTouchId && joyActive) {
          const dx = t.clientX - joyOrigin.x, dy = t.clientY - joyOrigin.y;
          const dist = Math.hypot(dx, dy);
          const maxR = 50;
          const angle = Math.atan2(dy, dx);
          const clampR = Math.min(dist, maxR);
          joyVec = { x: (Math.cos(angle) * clampR) / maxR, y: (Math.sin(angle) * clampR) / maxR };
          joyStick.style.left = `${50 + joyVec.x * 40}%`;
          joyStick.style.top = `${50 + joyVec.y * 40}%`;
        } else if (t.identifier === lookTouchId) {
          const dx = t.clientX - lookLast.x, dy = t.clientY - lookLast.y;
          camYaw -= dx * 0.0042;
          camPitch = Math.max(-1.35, Math.min(1.35, camPitch - dy * 0.0042));
          lookLast = { x: t.clientX, y: t.clientY };
        }
      }
    }, { passive: false });

    window.addEventListener('touchend', (e) => {
      for (let t of e.changedTouches) {
        if (t.identifier === joyTouchId) {
          joyActive = false; joyTouchId = null;
          joyBase.style.display = 'none'; joyVec = { x: 0, y: 0 };
        } else if (t.identifier === lookTouchId) {
          lookTouchId = null;
        }
      }
    });

    // Look Touch Zone (Right half of the screen)
    window.addEventListener('touchstart', (e) => {
      for (let t of e.changedTouches) {
        if (t.clientX > window.innerWidth * 0.45 && lookTouchId === null) {
          // Avoid registering touches that land on action buttons
          const targetTag = e.target.id;
          if (!targetTag.startsWith('btn-') && !e.target.classList.contains('btn-action')) {
            lookTouchId = t.identifier;
            lookLast = { x: t.clientX, y: t.clientY };
          }
        }
      }
    });

    // Action Buttons
    btnUse.addEventListener('click', executeInteraction);
    document.getElementById('btn-torch').addEventListener('click', () => {
      initAudio(); playBeep(640, 0.04);
      torchActive = !torchActive;
      torch.intensity = torchActive ? 2.8 : 0.0;
      document.getElementById('hud-torch-state').innerText = torchActive ? '[ON]' : '[OFF]';
      document.getElementById('hud-torch-state').style.color = torchActive ? '#ffd249' : '#888';
      document.getElementById('btn-torch').classList.toggle('active', torchActive);
    });
    document.getElementById('btn-sprint').addEventListener('click', () => {
      initAudio();
      isSprinting = !isSprinting;
      document.getElementById('btn-sprint').classList.toggle('active', isSprinting);
    });

    // 9. ANIMATION & GAME LOOP
    let lastTime = performance.now();
    let stepTimer = 0;
    let frameCount = 0, lastFpsTime = performance.now();

    function animate(now) {
      requestAnimationFrame(animate);
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      // FPS Counter
      frameCount++;
      if (now - lastFpsTime > 1000) {
        document.getElementById('hud-fps').innerText = `${frameCount} FPS`;
        frameCount = 0; lastFpsTime = now;
      }

      // Camera Rotation
      camera.rotation.order = 'YXZ';
      camera.rotation.y = camYaw;
      camera.rotation.x = camPitch;

      // Locomotion with Collision Clamping
      if (joyVec.x !== 0 || joyVec.y !== 0) {
        const speed = (isSprinting ? 5.2 : 2.8) * dt;
        const forward = new THREE.Vector3(0, 0, -1).applyAxisAngle(new THREE.Vector3(0, 1, 0), camYaw);
        const right = new THREE.Vector3(1, 0, 0).applyAxisAngle(new THREE.Vector3(0, 1, 0), camYaw);
        const move = forward.multiplyScalar(-joyVec.y * speed).add(right.multiplyScalar(joyVec.x * speed));

        camera.position.add(move);
        // Clamp to room bounds
        camera.position.x = Math.max(-halfW + 1.2, Math.min(halfW - 1.2, camera.position.x));
        camera.position.z = Math.max(-halfL + 1.2, Math.min(halfL - 1.2, camera.position.z));

        // Footsteps
        stepTimer += dt * (isSprinting ? 1.8 : 1.2);
        if (stepTimer > 0.48) { playStep(); stepTimer = 0; }
      }

      // Flashlight Follow Camera
      torch.position.copy(camera.position);
      const fwd = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
      torch.target.position.copy(camera.position).add(fwd.multiplyScalar(5));

      // Stasis Chamber Bioluminescent Pulse
      const pulse = 0.5 + 0.5 * Math.sin(now * 0.003);
      fluidMat.emissiveIntensity = 0.45 + pulse * 0.4;
      stasisLight.intensity = 1.2 + pulse * 0.8;

      // Dust Motes Slow Drift
      const posArr = dustGeo.attributes.position.array;
      for (let i = 1; i < dustCount * 3; i += 3) {
        posArr[i] -= 0.003;
        if (posArr[i] < 0) posArr[i] = roomH;
      }
      dustGeo.attributes.position.needsUpdate = true;

      // Raycast for interactables
      checkRaycast();

      renderer.render(scene, camera);
    }

    window.addEventListener('resize', () => {
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });

    requestAnimationFrame(animate);
  </script>
</body>
</html>
'''

# Write to APK assets and to repository root
apk_asset_path = r'C:\Users\USER\OneDrive\Desktop\antigravity\app\src\main\assets\index.html'
root_path = r'C:\Users\USER\OneDrive\Desktop\antigravity\index.html'

with open(apk_asset_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f'Wrote {len(html_content)} bytes to {apk_asset_path}')

with open(root_path, 'w', encoding='utf-8') as f:
    f.write(html_content)
print(f'Wrote {len(html_content)} bytes to {root_path}')
