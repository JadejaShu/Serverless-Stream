from Adarsh.vars import Var
from Adarsh.bot import StreamBot
from Adarsh.utils.human_readable import humanbytes
from Adarsh.utils.file_properties import get_file_ids
from Adarsh.server.exceptions import InvalidHash
import urllib.parse
import aiofiles
import logging
import aiohttp

logging.basicConfig(level=logging.INFO)
TEMPLATE_PATH_VIDEO = 'Adarsh/template/req.html'
TEMPLATE_PATH_AUDIO = 'Adarsh/template/req.html'
TEMPLATE_PATH_OTHER = 'Adarsh/template/dl.html'

async def render_page(id, secure_hash, quality='low'):
    file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
    if file_data.unique_id[:6] != secure_hash:
        logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
        logging.debug(f"Invalid hash for message with - ID {id}")
        raise InvalidHash

    filename = file_data.file_name
    src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(id)}')
    template_path = (
        TEMPLATE_PATH_VIDEO if file_data.mime_type.startswith('video') else
        TEMPLATE_PATH_AUDIO if file_data.mime_type.startswith('audio') else
        TEMPLATE_PATH_OTHER
    )

    async with aiofiles.open(template_path) as r:
        tag = file_data.mime_type.split('/')[0].strip()
        heading = (
            f'Watch {filename}' if tag == 'video' else
            f'Listen {filename}' if tag == 'audio' else
            f'Download {filename}'
        )
        html = (await r.read()).replace('tag', tag).format(heading, filename, src, quality)
        logging.info(f"1st HTML {html}")

    if tag == 'other':
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                heading = f'Download {filename}'
                file_size = humanbytes(int(u.headers.get('Content-Length')))
                async with aiofiles.open(TEMPLATE_PATH_OTHER) as r:
                    html = (await r.read()).format(heading, filename, src, quality)
                    logging.info(f"2nd HTML {html}")
                    
    current_url = f'{Var.URL}/{str(id)}/{filename}?hash={secure_hash}&quality={quality}'
    logging.info(f"{current_url}")
    html_code = f'''
    <p>
        <center><h5>Click on 👇 button to watch/download in your favorite player</h5></center>
        <center>
            <button onclick="window.location.href = '{current_url}'">Save in your gallery</button> &nbsp
        </center>
    </p>
    </p>
    <center>
        <h2>
            <a href="https://telegram.me/Mr_harsh_008">
                <img src="https://graph.org/file/b57cdba982191a25db535.jpg" alt="BotszList" width="150" height="75">
            </a>
        </h2>
    </center>
    '''

    html += html_code
    return html



# from Adarsh.vars import Var
# from Adarsh.bot import StreamBot
# from Adarsh.utils.human_readable import humanbytes
# from Adarsh.utils.file_properties import get_file_ids
# from Adarsh.server.exceptions import InvalidHash
# import urllib.parse
# import aiofiles
# import logging
# import aiohttp

# logging.basicConfig(level=logging.INFO)
# TEMPLATE_PATH_VIDEO = 'Adarsh/template/req.html'
# TEMPLATE_PATH_AUDIO = 'Adarsh/template/req.html'
# TEMPLATE_PATH_OTHER = 'Adarsh/template/dl.html'

# async def render_page(id, secure_hash, quality='low'):
#     file_data = await get_file_ids(StreamBot, int(Var.BIN_CHANNEL), int(id))
#     if file_data.unique_id[:6] != secure_hash:
#         logging.debug(f'link hash: {secure_hash} - {file_data.unique_id[:6]}')
#         logging.debug(f"Invalid hash for message with - ID {id}")
#         raise InvalidHash

#     src = urllib.parse.urljoin(Var.URL, f'{secure_hash}{str(id)}')
#     template_path = (
#         TEMPLATE_PATH_VIDEO if file_data.mime_type.startswith('video') else
#         TEMPLATE_PATH_AUDIO if file_data.mime_type.startswith('audio') else
#         TEMPLATE_PATH_OTHER
#     )

#     async with aiofiles.open(template_path) as r:
#         tag = file_data.mime_type.split('/')[0].strip()
#         heading = (
#             f'Watch {file_data.file_name}' if tag == 'video' else
#             f'Listen {file_data.file_name}' if tag == 'audio' else
#             f'Download {file_data.file_name}'
#         )
#         html = (await r.read()).replace('tag', tag).format(heading, file_data.file_name, src, quality)
#         logging.info(f"1st HTML {html}")

#     if tag == 'other':
#         async with aiohttp.ClientSession() as s:
#             async with s.get(src) as u:
#                 heading = f'Download {file_data.file_name}'
#                 file_size = humanbytes(int(u.headers.get('Content-Length')))
#                 async with aiofiles.open(TEMPLATE_PATH_OTHER) as r:
#                     html = (await r.read()).format(heading, file_data.file_name, src, quality)
#                     logging.info(f"2nd HTML {html}")
                    
#     current_url = f'{Var.URL}/{str(id)}/{file_data.file_name}?hash={secure_hash}&quality={quality}'
#     logging.info(f"{current_url}")
#     html_code = f'''
#     <p>
#         <center><h5>Click on 👇 button to watch/download in your favorite player</h5></center>
#         <center>
#             <button onclick="window.location.href = '{current_url}'">Save in your gallery</button> &nbsp
#         </center>
#     </p>
#     </p>
#     <center>
#         <h2>
#             <a href="https://telegram.me/Mr_harsh_008">
#                 <img src="https://graph.org/file/b57cdba982191a25db535.jpg" alt="BotszList" width="150" height="75">
#             </a>
#         </h2>
#     </center>
#     '''
#     html += html_code
#     return html
