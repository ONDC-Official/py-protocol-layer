def get_ack_response(context=None, ack=True, error=None):
    resp = {
        "context": context,
        "message":
            {
                "ack":
                    {
                        "status": "ACK" if ack else "NACK"
                    }
            }
    }
    resp.update({"error": error}) if error else None
    return resp