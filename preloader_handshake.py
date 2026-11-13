"""Task-local Preloader handshake: pair each byte with its own echo.
BROM continues to use the unmodified upstream handshake.
"""
import time,types

def paired_handshake(cdc, emit=print, retries=5):
    emit('Preloader handshake PID=%04x endpoints=%02x/%02x' % (cdc.pid,cdc.EP_OUT.bEndpointAddress,cdc.EP_IN.bEndpointAddress))
    cdc.set_line_coding(921600,0,8,1);cdc.setcontrollinestate(rts=True)
    for attempt in range(retries):
        try:
            for byte in b'\xa0\x0a\x50\x05':
                if cdc.EP_OUT.write(bytes([byte]),timeout=200)!=1:raise IOError('short USB write')
                echo=bytes(cdc.EP_IN.read(1,timeout=200))
                emit('handshake try=%d tx=%02x rx=%s' % (attempt+1,byte,echo.hex()))
                if echo!=bytes([byte^255]):raise IOError('echo mismatch')
            return True
        except Exception as exc:
            emit('handshake try=%d %s: %s' % (attempt+1,type(exc).__name__,exc))
            try:cdc.EP_IN.read(cdc.EP_IN.wMaxPacketSize,timeout=20)
            except Exception:pass
            time.sleep(.005)
    return False

def install(port):
    def run(self,retries=5):return paired_handshake(self.cdc,lambda line:print(line,flush=True),retries)
    port.run_handshake=types.MethodType(run,port)
