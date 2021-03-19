from client.ClientMat import *


if __name__ == '__main__':
    username = 'Ubiq071'
    key_ = 'S16HQxDGJVdktPVT'
    logger = simple_logger()

    c = Client(username, key_, logger, question_path="/Users/mark/PycharmProjects/MatClient/source/Question-client")
    c.main()
