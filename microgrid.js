// Interactive HTML5 Canvas Microgrid Renderer
document.addEventListener('DOMContentLoaded', function() {
  const canvas = document.getElementById('microgridCanvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;

  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    width = canvas.width;
    height = canvas.height;
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }

  resizeCanvas();
  window.addEventListener('resize', resizeCanvas);

  const displayWidth = () => canvas.width / window.devicePixelRatio;
  const displayHeight = () => canvas.height / window.devicePixelRatio;

  // Fetch live microgrid data from window or API
  let members = window.MICROGRID_MEMBERS || [];
  
  // Central AI Hub Node
  const getHubNode = () => ({
    id: 'ai-hub',
    name: 'AI Central Energy Hub',
    x: displayWidth() / 2,
    y: displayHeight() / 2,
    radius: 34,
    type: 'hub'
  });

  // Calculate positions for 7 house nodes around the hub
  function getHouseNodes() {
    const hub = getHubNode();
    const radiusDistance = Math.min(displayWidth(), displayHeight()) * 0.35;
    const count = members.length;

    return members.map((m, idx) => {
      const angle = (idx / count) * Math.PI * 2 - Math.PI / 2;
      return {
        ...m,
        x: hub.x + Math.cos(angle) * radiusDistance,
        y: hub.y + Math.sin(angle) * radiusDistance,
        radius: 26
      };
    });
  }

  // Energy Particles moving along grid lines
  const particles = [];
  const particleCount = 28;

  function initParticles(nodes) {
    const hub = getHubNode();
    particles.length = 0;

    nodes.forEach(node => {
      for (let i = 0; i < 4; i++) {
        particles.push({
          fromX: node.status === 'Producer' ? node.x : hub.x,
          fromY: node.status === 'Producer' ? node.y : hub.y,
          toX: node.status === 'Producer' ? hub.x : node.x,
          toY: node.status === 'Producer' ? hub.y : node.y,
          progress: Math.random(),
          speed: 0.004 + Math.random() * 0.006,
          color: node.status === 'Producer' ? '#00FF9D' : '#FFB800'
        });
      }
    });
  }

  let nodes = getHouseNodes();
  initParticles(nodes);

  // Animation Loop
  function animate() {
    const w = displayWidth();
    const h = displayHeight();
    ctx.clearRect(0, 0, w, h);

    nodes = getHouseNodes();
    const hub = getHubNode();

    // 1. Draw Connecting Radial Grid Lines
    nodes.forEach(node => {
      ctx.beginPath();
      ctx.moveTo(hub.x, hub.y);
      ctx.lineTo(node.x, node.y);
      ctx.strokeStyle = node.status === 'Producer' ? 'rgba(0, 255, 157, 0.25)' : 'rgba(255, 184, 0, 0.2)';
      ctx.lineWidth = 2;
      ctx.setLineDash([6, 6]);
      ctx.stroke();
      ctx.setLineDash([]);
    });

    // 2. Animate Energy Particles
    particles.forEach(p => {
      p.progress += p.speed;
      if (p.progress >= 1) p.progress = 0;

      const px = p.fromX + (p.toX - p.fromX) * p.progress;
      const py = p.fromY + (p.toY - p.fromY) * p.progress;

      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.shadowColor = p.color;
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;
    });

    // 3. Draw AI Energy Hub Node
    ctx.beginPath();
    ctx.arc(hub.x, hub.y, hub.radius, 0, Math.PI * 2);
    const hubGrad = ctx.createRadialGradient(hub.x, hub.y, 5, hub.x, hub.y, hub.radius);
    hubGrad.addColorStop(0, '#00F2FE');
    hubGrad.addColorStop(1, '#0F172A');
    ctx.fillStyle = hubGrad;
    ctx.strokeStyle = '#00F2FE';
    ctx.lineWidth = 3;
    ctx.shadowColor = '#00F2FE';
    ctx.shadowBlur = 20;
    ctx.fill();
    ctx.stroke();
    ctx.shadowBlur = 0;

    // AI Hub Icon text
    ctx.fillStyle = '#FFF';
    ctx.font = 'bold 11px Outfit';
    ctx.textAlign = 'center';
    ctx.fillText('AI HUB', hub.x, hub.y + 4);

    // 4. Draw House Nodes
    nodes.forEach(node => {
      // Glow circle
      ctx.beginPath();
      ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
      const isProducer = node.status === 'Producer' || node.status === 'Both';
      const glowColor = isProducer ? '#00FF9D' : '#FFB800';

      ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
      ctx.strokeStyle = glowColor;
      ctx.lineWidth = 2.5;
      ctx.shadowColor = glowColor;
      ctx.shadowBlur = 12;
      ctx.fill();
      ctx.stroke();
      ctx.shadowBlur = 0;

      // Solar Panel Accent for Producers
      if (isProducer) {
        ctx.beginPath();
        ctx.arc(node.x + 16, node.y - 16, 7, 0, Math.PI * 2);
        ctx.fillStyle = '#FFB800';
        ctx.fill();
      }

      // House Number
      ctx.fillStyle = '#FFF';
      ctx.font = 'bold 12px Plus Jakarta Sans';
      ctx.textAlign = 'center';
      ctx.fillText(`H-${node.houseNumber}`, node.x, node.y - 2);

      // kWh text below node
      ctx.fillStyle = glowColor;
      ctx.font = '600 10px Plus Jakarta Sans';
      ctx.fillText(`${node.availableEnergy} kWh`, node.x, node.y + 12);

      // Name Label below
      ctx.fillStyle = '#94A3B8';
      ctx.font = '500 11px Plus Jakarta Sans';
      ctx.fillText(node.name, node.x, node.y + 36);
    });

    requestAnimationFrame(animate);
  }

  animate();

  // Mouse Interactivity (Click Node to open Modal)
  const houseModal = document.getElementById('houseModal');
  const modalClose = document.getElementById('houseModalClose');

  canvas.addEventListener('click', function(e) {
    const rect = canvas.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    nodes.forEach(node => {
      const dist = Math.hypot(clickX - node.x, clickY - node.y);
      if (dist <= node.radius + 10) {
        openHouseModal(node);
      }
    });
  });

  function openHouseModal(node) {
    document.getElementById('modalMemberName').textContent = node.name;
    document.getElementById('modalHouseNum').textContent = `House ${node.houseNumber}`;
    document.getElementById('modalAvailable').textContent = `${node.availableEnergy} kWh`;
    document.getElementById('modalDemand').textContent = `${node.currentDemand} kWh`;
    document.getElementById('modalPrice').textContent = `₹${node.pricePerKwh}/kWh`;
    document.getElementById('modalStatusBadge').textContent = node.status;
    document.getElementById('modalStatusBadge').className = `badge badge-${node.status.toLowerCase()}`;

    const buyLink = document.getElementById('modalBuyLink');
    if (buyLink) {
      buyLink.href = `/trading?seller=${node.username}`;
    }

    if (houseModal) houseModal.classList.add('active');
  }

  if (modalClose && houseModal) {
    modalClose.addEventListener('click', () => houseModal.classList.remove('active'));
  }
});
