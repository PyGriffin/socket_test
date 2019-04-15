import socket
import re
import select


def porcess_html(new_socket, request):
    # 提取文件名
    date_list = request.splitlines()
    res = re.match(r'[^/]+(/[^ ]*)', date_list[0])
    file_name = ''
    if res:
        file_name = res.group(1)
        print(file_name)
        if file_name == '/':
            file_name = './html/index.html'
        try:
            f = open('./html{}'.format(file_name), 'rb')
        except Exception as e:
            response_body = '---not files---'

            response_header = 'HTTP/1.1 200 OK\r\n'
            response_header += 'Content-Length:%d\r\n' % len(response_body)
            response_header += '\r\n'
            new_socket.send(response_header.encode('utf-8') + response_body)
        else:
            html = f.read()
            f.close()

            response_body = html

            response_header = 'HTTP/1.1 200 OK\r\n'
            response_header += 'Content-Length:%d\r\n'%len(response_body)
            response_header += '\r\n'
            new_socket.send(response_header.encode('utf-8')+response_body)


def main():
    # 创建套接字
    tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #　绑定服务器ｉｐ
    ip = '127.0.0.1'
    port = 8081
    tcp_server_socket.bind((ip, port))

    # 主动变被动监听
    tcp_server_socket.listen(128)

    # 创建epoll空间
    epl = select.epoll()
    # 将套接字对应的fd注册到epoll中
    epl.register(tcp_server_socket.fileno(), select.EPOLLIN)

    # 新客户端对应的套接字字典
    new_socket_fd_dict = dict()

    # 循环为不同的客户端服务
    while True:
        # epoll默认堵塞,直到监测到数据的到来 通过事件通知 告诉这个程序,
        # 返回一个列表[(fd,event),(fd,event)] (套接字对应的文件描述符,对应的事件,例如recv)
        fd_socket_list = epl.poll()

        # 遍历列表判断事件类型
        for fd, event in fd_socket_list:
            #　等待新客户端链接
            if fd == tcp_server_socket.fileno():
                new_socket, client_add = tcp_server_socket.accept()
                # 将新的套接字注册到epoll中
                epl.register(new_socket.fileno(), select.EPOLLIN)
                new_socket_fd_dict[new_socket.fileno()] = new_socket

            # 如果不是主套接字的事件,则是客户套接字接收到了消息
            elif event == select.EPOLLIN:

                recv_date = new_socket_fd_dict[fd].recv(1024).decode('utf-8')
                if recv_date:
                    # 函数处理返回的信息
                    porcess_html(new_socket_fd_dict[fd], recv_date)
                # 客户端关闭后注销该套接字的epoll
                else:
                    new_socket_fd_dict[fd].close()
                    epl.unregister(fd)
                    del new_socket_fd_dict[fd]
    tcp_server_socket.close()

if __name__ == '__main__':
    main()