# ... (existing imports and code)

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
        html = (await r.read()).replace('tag', tag) % (heading, file_data.file_name, src, quality)

    if tag == 'other':
        async with aiohttp.ClientSession() as s:
            async with s.get(src) as u:
                heading = f'Download {file_data.file_name}'
                file_size = humanbytes(int(u.headers.get('Content-Length')))
                async with aiofiles.open(TEMPLATE_PATH_OTHER) as r:
                    html = (await r.read()) % (heading, file_data.file_name, src, file_size, quality)

    current_url = f'{Var.URL}/{str(id)}/{file_data.file_name}?hash={secure_hash}&quality={quality}'
    html_code = f'''
    <p>
        <center><h5>Click on 👇 button to watch/download in your favorite player</h5></center>
        <center>
            <button style="font-size: 20px; background-color: skyblue; border-radius: 10px;" onclick="window.location.href = 'intent:{current_url}#Intent;package=com.mxtech.videoplayer.ad;S.title={file_data.file_name};end'">MX player</button> &nbsp
            <button style="font-size: 20px; background-color: orange; border-radius: 10px;" onclick="window.location.href = 'vlc://{current_url}'">VLC player</button> &nbsp <br>
            <p>&nbsp</p>
            <button style="font-size: 20px; background-color: red; border-radius: 10px;" onclick="window.location.href = 'playit://playerv2/video?url={current_url}&amp;title={file_data.file_name}'">Playit player</button> &nbsp <br>
            <p>&nbsp</p>
            <button style="font-size: 20px; background-color: yellow; border-radius: 10px;" onclick="window.location.href = '{current_url}'">Save in your gallery</button> &nbsp
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
