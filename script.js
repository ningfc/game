const canvas = document.getElementById('fireworksCanvas');
const ctx = canvas.getContext('2d');

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

class Particle {
    constructor(x, y, color) {
        this.x = x;
        this.y = y;
        this.color = color;
        this.radius = Math.random() * 2 + 1;
        this.speed = Math.random() * 5 + 2;
        this.angle = Math.random() * 2 * Math.PI;
        this.vx = Math.cos(this.angle) * this.speed;
        this.vy = Math.sin(this.angle) * this.speed;
        this.alpha = 1;
        this.decay = Math.random() * 0.015 + 0.007;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.alpha -= this.decay;
    }
    draw() {
        ctx.save();
        ctx.globalAlpha = this.alpha;
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, 2*Math.PI);
        ctx.fillStyle = this.color;
        ctx.fill();
        ctx.restore();
    }
}

const particles = [];
function createFirework(x, y) {
    const numParticles = 50 + Math.floor(Math.random() * 50);
    const color = `hsl(${Math.floor(Math.random() * 360)}, 100%, 50%)`;
    for (let i = 0; i < numParticles; i++) {
        particles.push(new Particle(x, y, color));
    }
}

// 新增 Rocket 类，用于从地面发射烟花火箭
class Rocket {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = canvas.height;
        this.vx = (Math.random() - 0.5) * 2;
        this.vy = -(Math.random() * 3 + 7); // 初始向上速度
        this.gravity = 0.05;
    }
    update() {
        this.x += this.vx;
        this.y += this.vy;
        this.vy += this.gravity;
    }
    draw() {
        ctx.save();
        ctx.beginPath();
        ctx.arc(this.x, this.y, 3, 0, 2 * Math.PI);
        ctx.fillStyle = 'white';
        ctx.fill();
        ctx.restore();
    }
}

const rockets = [];
function createRocket() {
    rockets.push(new Rocket());
}

function animate() {
    requestAnimationFrame(animate);
    // 清除画布但留下轻微拖影效果
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 更新并绘制火箭
    for (let i = rockets.length - 1; i >= 0; i--) {
        const r = rockets[i];
        r.update();
        // 当火箭停止上升时触发爆炸
        if (r.vy >= 0) {
            createFirework(r.x, r.y);
            rockets.splice(i, 1);
        } else {
            r.draw();
        }
    }

    // 更新并绘制粒子
    for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.update();
        if (p.alpha <= 0) {
            particles.splice(i, 1);
        } else {
            p.draw();
        }
    }
}

// 自动触发随机烟花效果（保留原有效果）
setInterval(() => {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height * 0.5; // 上半屏显示
    createFirework(x, y);
}, 800);

// 新增自动触发火箭发射效果，每隔1200ms从地面发射一枚火箭
setInterval(() => {
    createRocket();
}, 1200);

// 点击触发烟花效果
canvas.addEventListener('click', (e) => {
    createFirework(e.clientX, e.clientY);
});

animate();
