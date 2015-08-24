import png

class Image:
    def __init__( self, w, h, pixels = None, metadata = None, bpp = None ):
        self.w = w
        self.h = h
        if metadata is None:
            if bpp == 4:
                self.metadata = {'interlace': 0, 'greyscale': False, 'gamma': 0.45455, 'alpha': True, 'planes': 4, 'bitdepth': 8 }
            else:
                self.metadata = {'interlace': 0, 'greyscale': False, 'gamma': 0.45455, 'alpha': False, 'planes': 3, 'bitdepth': 8 }
        else:
            self.metadata = metadata

        assert self.metadata['bitdepth'] == 8

        self.pixels = bytearray( self.totalBytes ) if pixels is None else pixels

    def I( self, x, y ):
        return ( ( int( y ) * self.w ) + int( x ) ) * self.bytesPerPixel

    @property
    def stride( self ):
        return self.w * self.bytesPerPixel

    @property
    def totalBytes( self ):
        return self.w * self.h * self.bytesPerPixel

    @property
    def bits( self ):
        return self.bitdepth * self.planes
    @property
    def bytesPerPixel( self ):
        return self.planes

    def __getattr__( self, key ):
        return self.metadata[key]

    def copyWithNewBpp( self, newBpp ):
        newMeta = self.metadata.copy()

        newMeta['planes'] = newBpp
        newMeta['alpha'] = ( newBpp == 4 )

        new = Image( self.w, self.h, None, newMeta )

        if newBpp == self.bytesPerPixel:
            for i in range( self.totalBytes ):
                new.pixels[i] = self.pixels[i]
        elif newBpp > self.bytesPerPixel:
            for i in range( self.w * self.h ):
                destI = i * 4
                sourceI = i * 3

                new.pixels[destI+0] = self.pixels[sourceI+0]
                new.pixels[destI+1] = self.pixels[sourceI+1]
                new.pixels[destI+2] = self.pixels[sourceI+2]
                new.pixels[destI+3] = 255
        else:
            for i in range( self.w * self.h ):
                destI = i * 3
                sourceI = i * 4

                new.pixels[destI+0] = self.pixels[sourceI+0]
                new.pixels[destI+1] = self.pixels[sourceI+1]
                new.pixels[destI+2] = self.pixels[sourceI+2]

        return new


    @staticmethod
    def read( filename ):
        source = png.Reader( filename=filename )
        w, h, pixels, metadata = source.read_flat()
        return Image( w, h, pixels, metadata )

    def save( self, name ):
        output = open( name, 'wb' )
        writer = png.Writer( self.w, self.h, **self.metadata )
        writer.write_array( output, self.pixels )
        output.close()

CHUNKSIZE = 16

def blit16x16( source, dest, sourceStart, destStart ):
    assert source.bytesPerPixel == dest.bytesPerPixel

    rowTuple = tuple( range( CHUNKSIZE * source.bytesPerPixel ) )

    for y in range( CHUNKSIZE ):
        for x in rowTuple:
            dest.pixels[x + destStart] = source.pixels[x + sourceStart]
        sourceStart += source.stride
        destStart += dest.stride

arg1 = Image.read( 'water.png' )
arg2 = Image.read( 'desert.png' )
mask = Image.read( 'Layout.png' )

arg1 = arg1.copyWithNewBpp( 3 )
arg2 = arg2.copyWithNewBpp( 3 )

output = Image( mask.w, mask.h, None, metadata = None, bpp = 3 )
sourceStride = arg1.stride

for i in range( 0, output.totalBytes, 3 ):
    _i = i / 3
    srcI = arg1.I( int( _i % output.w ) % arg1.w, int( _i // output.w ) % arg1.h )

    cur = tuple( mask.pixels[i:i+3] )
    if cur == ( 0, 0, 0 ):
        output.pixels[i:i+3] = arg1.pixels[srcI:srcI+3]
    elif cur == ( 255, 255, 255 ):
        output.pixels[i:i+3] = arg2.pixels[srcI:srcI+3]
    else:
        output.pixels[i:i+3] = mask.pixels[i:i+3]

sections = {
    'a': ( 0, 0 ), 'b': ( 16, 0 ), 'c': ( 32, 0 ), 'd': ( 48, 0 ),
    'e': ( 0, 16 ), 'f': ( 16, 16 ), 'g': ( 32, 16 ), 'h': ( 48, 16 ),
    'j': ( 0, 32 ), 'k': ( 16, 32 ), 'l': ( 32, 32 ), 'm': ( 48, 32 ),
    'n': ( 0, 48 ), 'o': ( 16, 48 ), 'p': ( 32, 48 ), 'q': ( 48, 48 ),

    'r': ( 64, 0 ), 's': ( 80, 0 ),
    't': ( 64, 16 ), 'u': ( 80, 16 ),
    }
outputSections = ( 'abcdabcdjmadjmcb',
        'efgheuthnqehehpo',
        'jklmjsrmabcdlsrk',
        'nopqnopqnopqtfgu',
        'rmjsrklsjklmrscb',
        'ghefpopoefghpotu',
        'lmjkcbcbcblkrmjs',
        'theutfgugfpotheu',
        'lsrkrslklklkrslk',
        'tutugftugutftugf',
        'rsrsrklslsrkadlk',
        'gutftfgugfgfnqgf',
        '0000000000lklklk',
        '0000000000gfgfgf', )

output.save( 'out_minimal.png' )

sections = { key: output.I( *sections[key] ) for key in sections }


fullOutput = Image( len(outputSections[0])*16, len(outputSections)*16, None, bpp = 3 )
print( fullOutput.w, fullOutput.h )

y = 0
for line in outputSections:
    x = 0
    for section in line:
        if section in sections:
            blit16x16( output, fullOutput, sections[section], fullOutput.I( x, y ) )
        x += 16
    y += 16

fullOutput.save( 'out.png' )
