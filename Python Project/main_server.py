# Python server to interact with Unity

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json

import UrbanMovementModel as UrbanM

WIDTH = 10000
HEIGHT = 5000
INTERSECT_DIST = 400
PROB_SPAWN = 0.01
MAX_TIME_ON = 40
MAX_TIME_OFF = 150
SEED = 1
INTELLIGENT = True

model = UrbanM.UrbanMovementModel(PROB_SPAWN, WIDTH, HEIGHT, INTERSECT_DIST, MAX_TIME_ON, MAX_TIME_OFF, SEED, INTELLIGENT)

def updateModel():
    model.step()
    (car_positions, traffic_lights) = model.get_agents()
    json = positionsToJSON(car_positions, traffic_lights)
    print(json)
    return json

def positionsToJSON(car_positions, traffic_lights):
    DICT = []
    for position in car_positions:
        pos = {
            "x" : position[0],
            "z" : position[1],
            "y" : 0
        }
        DICT.append(pos)
    return json.dumps(DICT)


class Server(BaseHTTPRequestHandler):
    
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = json.loads(self.rfile.read(content_length))
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                     str(self.path), str(self.headers), json.dumps(post_data))
        
        positionsJSON = updateModel()
        self._set_response()
        resp = "{\"cars\":" + positionsJSON + "}"
        #print(resp)
        self.wfile.write(resp.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=Server, port=8585):
    logging.basicConfig(level=logging.INFO)
    server_address = ('',port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n") # HTTPD is HTTP Daemon!
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:   # CTRL+C stops the server
        pass
    httpd.server_close()
    logging.info("Stopping httpd...\n")

if __name__ == '__main__':
    from sys import argv
    run(port=8080)
    # if len(argv) == 2:
    #     run(port=int(argv[1]))
    # else:
    #     run()