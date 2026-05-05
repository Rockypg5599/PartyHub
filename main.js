const config = {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: "#000000",
    physics: { default: "arcade" },
    scene: { preload, create, update }
};

const game = new Phaser.Game(config);

let player, bullets, enemies, cursors, spaceKey;

function preload() {
    this.load.image("player", "https://labs.phaser.io/assets/sprites/block.png");
    this.load.image("bullet", "https://labs.phaser.io/assets/sprites/pixel.png");
    this.load.image("enemy", "https://labs.phaser.io/assets/sprites/block.png");
}

function create() {
    player = this.physics.add.sprite(400, 500, "player").setTint(0x00ff00);

    bullets = this.physics.add.group();
    enemies = this.physics.add.group();

    cursors = this.input.keyboard.createCursorKeys();
    spaceKey = this.input.keyboard.addKey(
        Phaser.Input.Keyboard.KeyCodes.SPACE
    );

    // spawn enemies
    this.time.addEvent({
        delay: 1000,
        loop: true,
        callback: () => {
            let x = Phaser.Math.Between(50, 750);
            let enemy = enemies.create(x, 0, "enemy").setTint(0x00ff00);
            enemy.setVelocityY(100);
        }
    });

    // collisions
    this.physics.add.overlap(bullets, enemies, (b, e) => {
        b.destroy();
        e.destroy();
    });
}

function update() {
    player.setVelocity(0);

    if (cursors.left.isDown) player.setVelocityX(-300);
    if (cursors.right.isDown) player.setVelocityX(300);
    if (cursors.up.isDown) player.setVelocityY(-300);
    if (cursors.down.isDown) player.setVelocityY(300);

    if (Phaser.Input.Keyboard.JustDown(spaceKey)) {
        let bullet = bullets.create(player.x, player.y - 20, "bullet");
        bullet.setVelocityY(-400);
        bullet.setTint(0x00ff00);
    }
}