def get_ack_response(ack=True, error=None):
    return {
        "context": None,
        "message":
            {
                "ack": "ACK" if ack else "NACK"
            },
        "error": error,
    }
