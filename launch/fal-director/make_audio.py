"""Prepare the three exact Japanese voice lines before spending fal credit."""
import asyncio
from pathlib import Path
import edge_tts

async def main():
    folder = Path(__file__).parent / 'assets/audio'
    folder.mkdir(parents=True, exist_ok=True)
    lines = ['まって。これは、いちねんまえ？', 'これをしまいます。', 'みさきにでんわします。']
    for index, text in enumerate(lines):
        path = folder / f'{index}.mp3'
        if not path.exists():
            await edge_tts.Communicate(text, 'ja-JP-NanamiNeural', rate='-10%').save(str(path))
        print(f'Ready: {path.name}')

if __name__ == '__main__':
    asyncio.run(main())
