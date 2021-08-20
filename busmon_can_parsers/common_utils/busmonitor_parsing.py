def arb_id_str_to_bytearray(arb_id: str) -> bytearray:
    arb_id = "0"*(8 - len(arb_id)) + arb_id  # pad with zeros
    return bytearray.fromhex(arb_id)


def payload_str_to_bytearray(payload: str) -> bytearray:
    return bytearray.fromhex(payload.replace("  ", ""))
