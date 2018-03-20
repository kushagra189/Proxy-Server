import socket
import os , os.path
import httplib
import requests
# import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

host = ""
portr = 20000
ports = 12345

def get_status_code(host, path):
    """ This function retreives the status code of a website by requesting
        HEAD data from the host. This means that it only requests the headers.
        If the host cannot be reached or something else goes wrong, it returns
        None instead.
    """
    try:
        conn = httplib.HTTPConnection(host)
        conn.request("HEAD", path)
        return conn.getresponse().status
    except StandardError:
        return None

#server binds to port 12345
s.bind((host, ports))
s.listen(5)

print('Server listening....')

while True:

    #setting up client
    r = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

    #client connects to main server
    try:
        r.connect((host, portr))
    except Exception as e:
        print('Server error')
        # time.sleep(6)

    #server accepting connection from browser
    conn, addr = s.accept()

    #the caching array
    cache = []
    cache_date = []
    try:
        with open("cache", "r") as cache_var:
            cache = [w.strip() for w in cache_var.readlines()]
            print('\n')
            print(cache)
    except:
        print("Cache doesn't exist")

    #receiving request from browser
    data = conn.recv(1024)



    data = data.decode('utf-8')

    if "http://localhost:" not in data:
        continue
    temp = data.split( )[1]
    filename = temp.split("/")[3]
    print(data)
    print filename
    req1 = requests.get("http://localhost:20000/" + filename )
    # print req1.headers['Last-Modified']

        # prints the int of the status code. Find more at httpstatusrappers.com :)
    get_status_code("localhost" , filename)
    if filename in cache:
        req = requests.head("http://localhost:20000/" + filename)
        print req
        print(req.status_code)

        date_modified =  cache.index(filename) + 1
        # print cache[date_modified]
        if cache[date_modified] != req1.headers['Last-Modified']:
            print req1.headers['Last-Modified']
            cache.remove(cache[date_modified])
            cache.remove(cache[date_modified-1])

            cache.append(filename)
            cache.append((req1.headers['Last-Modified']))
            with open("cache", "w") as cache_var:
                cache_list = "\n".join(cache)#.join(cache_date)
                cache_list += "\n".join("\n")
                cache_list += "\n".join(cache_date)
                cache_var.write(cache_list)

            os.remove(filename)

            request = data.replace("http://localhost:" + str(portr), "")
            r.send(bytearray(request, 'utf-8'))

            #recieving response from main server
            response = b''
            while True:
                packet = r.recv(1024)
                if not packet:
                    break
                response += packet
            with open(filename, "wb") as new_file:
                new_file.write(response)
            conn.send(response)

        else:
            print(filename + " in cache")

            #open file in cache
            try:
                with open(filename, "rb") as f:
                    cache_response = f.read()
            except Exception as e:
                print("Error opening the file from cache")
                print(e)
                cache.remove(filename)

        #send response to browser
            conn.send(cache_response)

    else:
        if filename != 'favicon.ico':
            print(filename + " not in cache")

            #forwarding request to main server

            if os.path.isfile(filename):
                print "file not found"
            else:
                request = data.replace("http://localhost:" + str(portr), "")
                r.send(bytearray(request, 'utf-8'))

                #recieving response from main server
                response = b''
                while True:
                    packet = r.recv(1024)
                    if not packet:
                        break
                    response += packet

                #storing new file into cache
                if filename != '':
                    #cache length is maxinmum of 3
                    # if (cache[0] not None):
                    #     if cache[0] == '':
                    #         cache.remove(cache[0])
                    if len(cache) < 6:
                        cache.append(filename)
                        cache_date.append(req1.headers['Last-Modified'])
                    else:
                        cache.append(filename)
                        cache_date.append(req1.headers['Last-Modified'])
                        temp_file = cache[0]
                        temp_file1 = cache[1]
                        cache.remove(temp_file1)
                        cache.remove(temp_file)
                        #remove the old file from the directory
                        try:
                            os.remove(temp_file)
                        except Exception as e:
                            print(e)
                            print("ERROR: " + temp_file + " does not exist")

                    #create new file for new entry in cache
                    with open(filename, "wb") as new_file:
                        new_file.write(response)

                #send response to browser
                conn.send(response)

            #update cache file with new entries
                with open("cache", "w") as cache_var:
                    cache_list = "\n".join(cache)#.join(cache_date)
                    cache_list += "\n".join("\n")
                    cache_list += "\n".join(cache_date)
                    cache_var.write(cache_list)
        else:
            pass
    #close the server connection and client connection
    conn.close()
    r.close()
