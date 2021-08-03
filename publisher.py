import os
import aiofiles
from sanic import Sanic
from sanic import response
import config
import aioredis
import random

app = Sanic("file server")


@app.listener('before_server_start')
async def setup_db(app, loop):
    config.redis_con = await aioredis.create_redis_pool('redis://localhost')


async def upload_handler(request, url):
    if not os.path.exists(config.uploads_dir):
        os.makedirs(config.uploads_dir)
    for file_item in request.files:
        for file_data in request.files[file_item]:
            generated_file_name = str(random.getrandbits(256))
            print("handling upload : " + str(file_data.name))
            async with aiofiles.open(config.uploads_dir + "/" + generated_file_name, 'wb') as file:
                await file.write(file_data.body)
                await file.close()
            task = {"file_name": generated_file_name,
                    "original_name": file_data.name}
            await config.redis_con.publish_json('file_tasks', task)
    return response.json({"status": "ok"})


app.add_route(upload_handler, '/upload/<url>', methods=['POST'])

app.run(host='0.0.0.0', port=8082, debug=False, workers=10)
