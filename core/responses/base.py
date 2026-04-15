from rest_framework.response import Response


def success(data=None, message="success", status=200):
    return Response({
        "status": "success",
        "message": message,
        "data": data
    }, status=status)


def error(message="error", status=400, data=None):
    return Response({
        "status": "error",
        "message": message,
        "data": data
    }, status=status)
