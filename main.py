import asyncio
import traceback


async def main():
    try:
        import pygame
        import hacker

        await hacker.main()
    except Exception:
        error = traceback.format_exc()
        print(error)
        try:
            import pygame

            pygame.init()
            screen = pygame.display.set_mode((900, 600))
            font = pygame.font.SysFont("consolas", 16)
            lines = ["HackerArena crashed during startup:", *error.splitlines()[-24:]]
            while True:
                screen.fill((30, 30, 30))
                for index, line in enumerate(lines):
                    text = font.render(line[:110], True, (255, 80, 80) if index == 0 else (240, 240, 240))
                    screen.blit(text, (18, 18 + index * 22))
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                await asyncio.sleep(0)
        except Exception:
            raise


asyncio.run(main())
