# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import mat_pb2 as mat__pb2


class MatStub(object):
    """The greeting service definition.
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mat.proto
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.login = channel.unary_unary(
                '/Mat/login',
                request_serializer=mat__pb2.LoginRequest.SerializeToString,
                response_deserializer=mat__pb2.UserLoginResponse.FromString,
                )
        self.GameStream = channel.stream_stream(
                '/Mat/GameStream',
                request_serializer=mat__pb2.ActionRequest.SerializeToString,
                response_deserializer=mat__pb2.ActionResponse.FromString,
                )


class MatServicer(object):
    """The greeting service definition.
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mat.proto
    """

    def login(self, request, context):
        """Sends a greeting
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GameStream(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MatServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'login': grpc.unary_unary_rpc_method_handler(
                    servicer.login,
                    request_deserializer=mat__pb2.LoginRequest.FromString,
                    response_serializer=mat__pb2.UserLoginResponse.SerializeToString,
            ),
            'GameStream': grpc.stream_stream_rpc_method_handler(
                    servicer.GameStream,
                    request_deserializer=mat__pb2.ActionRequest.FromString,
                    response_serializer=mat__pb2.ActionResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Mat', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Mat(object):
    """The greeting service definition.
    python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. mat.proto
    """

    @staticmethod
    def login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mat/login',
            mat__pb2.LoginRequest.SerializeToString,
            mat__pb2.UserLoginResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GameStream(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/Mat/GameStream',
            mat__pb2.ActionRequest.SerializeToString,
            mat__pb2.ActionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
