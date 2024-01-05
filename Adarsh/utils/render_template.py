from Adarsh.vars import Var
from Adarsh.bot import StreamBot
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.file_properties import get_file_ids
from Adarsh.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp

TEMPLATE_PATH_VIDEO = 'Adarsh/template/req.html'
TEMPLATE_PATH_AUDIO = 'Adarsh/template/req.html'
TEMPLATE_PATH_OTHER = 'Adarsh/template/dl.html'

async def render_page(id, secure_hash, quality='low'):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(id)}')
    template_path = (
        TEMPLATE_PATH_VIDEO if file_data.mime_type.startswith('video') else
        TEMPLATE_PATH_AUDIO if file_data.mime_type.startswith('audio') else
        TEMPLATE_PATH_OTHER
    )

    async with aiofiles.open(template_path) as r:
        tag = file_data.mime_type.split('/')[0].strip()
        heading = (
            f'Watch {file_data.file_name}' if tag == 'video' else
            f'Listen {file_data.file_name}' if tag == 'audio' else
            f'Download {file_data.file_name}'
        )
        html = (await r.read()).replace('tag', tag) % (file_data.file_name, file_data.file_name, src, quality)

    if tag == 'other':
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                heading = f'Download {file_data.file_name}'
                file_size = humanbytes(int(u.headers.get('Content-Length')))
                async with aiofiles.open(TEMPLATE_PATH_OTHER) as r:
                    html = (await r.read()) % (heading, file_data.file_name, src, file_size)

    current_url = f'{Var.URL}/{str(id)}/{file_data.file_name}?hash={secure_hash}&quality={quality}'
    html_code = (
    '<p>\n'
    '    <center><h5>Click on 👇 button to watch/download in your favorite player</h5></center>\n'
    '    <center>\n'
    '        <button class="cybr-btn player" style="font-size: 20px; background-color: skyblue; border-radius: 10px;" '
    'data-plyr-provider="html" data-plyr-embed-id="{current_url}">Play Video</button> &nbsp\n'
    '    </center>\n'
    '</p>\n'
    '<p>\n'
    '    <center>\n'
    '        <!-- Add quality selection dropdown -->\n'
    '        <select id="quality-selector">\n'
    '            <option value="low">Low Quality</option>\n'
    '            <option value="medium">Medium Quality</option>\n'
    '            <option value="high">High Quality</option>\n'
    '        </select>\n'
    '    </center>\n'
    '</p>\n'
    '<script src="https://cdn.plyr.io/3.6.12/plyr.js"></script>\n'
    '<script>\n'
    '    document.addEventListener(\'DOMContentLoaded\', () => {{\n'
    '        const players = Plyr.setup(\'.player\', {{\n'
    '            controls: [\'play-large\', \'play\', \'progress\', \'current-time\', \'mute\', \'volume\', \'fullscreen\'],\n'
    '        }});\n'
    '\n'
    '        const qualitySelector = document.getElementById(\'quality-selector\');\n'
    '        qualitySelector.addEventListener(\'change\', function() {{\n'
    '            const selectedQuality = this.value;\n'
    '            const downloadButton = document.querySelector(\'.cybr-btn\');\n'
    '            const newDownloadURL = downloadButton.href.replace(\'{quality}\', selectedQuality);\n'
    '            downloadButton.href = newDownloadURL;\n'
    '        }});\n'
    '        qualitySelector.value = \'{quality}\';\n'
    '    }});\n'
    '</script>'
)
    formatted_html_code = html_code.format(current_url=current_url, quality=quality)
    return html + formatted_html_code
