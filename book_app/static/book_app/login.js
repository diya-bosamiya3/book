const canvas = document.getElementById("bookCanvas");
const ctx = canvas.getContext("2d");

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const pages = [];

function spawnPage() {
  const page = {
    x: Math.random() * canvas.width,
    y: -20,
    speed: 0.5 + Math.random() * 1,
    size: 20 + Math.random() * 30,
    angle: Math.random() * Math.PI * 2,
    rotationSpeed: 0.01 + Math.random() * 0.02
  };
  pages.push(page);
}

function drawPage(page) {
  ctx.save();
  ctx.translate(page.x, page.y);
  ctx.rotate(page.angle);
  ctx.fillStyle = "rgba(255, 255, 255, 0.8)";
  ctx.fillRect(-page.size / 2, -page.size / 2, page.size, page.size * 1.4);
  ctx.restore();
}

function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  pages.forEach((page, index) => {
    page.y += page.speed;
    page.angle += page.rotationSpeed;
    drawPage(page);
    if (page.y > canvas.height + 50) pages.splice(index, 1);
  });

  if (Math.random() < 0.1) spawnPage();

  requestAnimationFrame(animate);
}

animate();

window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
