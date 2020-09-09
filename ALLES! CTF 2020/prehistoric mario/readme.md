# prehistoric mario
> Category: Reverse Engineering

> Difficulty: Medium

> Author: 0x4d5a

Fred Flintstone was the real OG. And he played mario, at least thats how I imagine it.

Anyway, Fred is occupied. Help his dino to trigger the right boxes. Flag is all Caps.

> Challenge Files:prehistoric-mario.apk

# Writeup

Used tools: 
- https://github.com/vaibhavpandeyvpz/apkstudio.git
- https://bintray.com/skylot/jadx/releases/v1.1.0#files

I used apkstudio to decompile the apk, from doing an initial analysis the code that stood out was the `MyPlatformer` class, which was a `.smali` file. As I don't like to suffer I used jadx to decompile the `.smali` to `.java` code.

After analyzing the code I conclude that there were 2 ways of solving this challenge, the first which was maybe the intended way and the second one which I like to call "Hell no just give that flag". I would like to say I went with the first method but I didn't. In any case doing things by the book we were supposed to understand the sequence of the `?` blocks and configure the proper colors on each available one, then finally we would need to find a different tile (the 1337 rainbow tile) that would trigger the check_flag and if all was ok the map would be reloaded to the final map containing the flag.

The key function of this challenge is this function:

```java
private void checkFlag() {
        MessageDigest messageDigest;
        int intValue;
        byte[] bArr = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
        TiledMapTileLayer tiledMapTileLayer = this.map.getLayers().get("questionmarks");
        int i = 0;
        int i2 = 0;
        while (i < 100) {
            int i3 = i2;
            for (int i4 = 0; i4 < 100; i4++) {
                TiledMapTileLayer.Cell cell = tiledMapTileLayer.getCell(i, i4);
                if (!(cell == null || !cell.getTile().getProperties().containsKey("questionmarkType") || (intValue = ((Integer) cell.getTile().getProperties().get("questionmarkType")).intValue()) == 1337)) {
                    bArr[i3] = (byte) intValue;
                    i3++;
                }
            }
            i++;
            i2 = i3;
        }
        try {
            messageDigest = MessageDigest.getInstance("SHA-256");
        } catch (NoSuchAlgorithmException e) {
            e.printStackTrace();
            messageDigest = null;
        }
        messageDigest.update(bArr);
        messageDigest.update("P4ssw0rdS4lt".getBytes());
        if (toHex(messageDigest.digest()).equals("024800ace2ec394e6af68baa46e81dfbea93f0f6730610560c66ee9748d91420")) {
            try {
                messageDigest.update(bArr);
                messageDigest.update("P4ssw0rdS4lt".getBytes());
                messageDigest.update(bArr);
                byte[] digest = messageDigest.digest();
                byte[] decode = Base64Coder.decode(Gdx.files.internal("flag_enc").readString());
                SecretKeySpec secretKeySpec = new SecretKeySpec(digest, 0, digest.length, "RC4");
                Cipher instance = Cipher.getInstance("RC4");
                instance.init(2, secretKeySpec, instance.getParameters());
                String str = new String(instance.doFinal(decode));
                FileHandle local = Gdx.files.local("map_flag.tmx");
                local.writeString(str, false);
                Gdx.files.local("tileSet.png").writeBytes(Base64Coder.decode("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T5/+BQOY8/xvJtwPAAADAFBMVEUAAAAZGRkXPDQoJygnOzw6OjoNUisGWzUaSDcVWjUDbjgpSD0qUj44RD4kZzwOcUUZf2QsTEAsVkA0S0M1WEc+WlAtZ0EvcUI5Yks+YVAweEMyfFpBOz5SHmlVIm1oN3VIR0dIWElBW1NWWEtYV1lcWmFDZktHaFhSYE9ZZVROb2BSbGJZd2lmV01qXFVxXFdiXWBsYlloc119Y0t1ZFh6eVRqaWlqdWdlfXR8bGF0aXF6cmd6eXk5NokFV70MZb4pU50rW6EpY543dKQHUsERaMQlb8tHSY9JeqwSjDIjkjwmoz4BkkUTgmEFpEsnjEEmlEAyh0Q0mEYggWYnqEUns0o2p0c5t0o9slE7xUs91E1KlFdJsFB9ik5phHd8hG1win5itV5otWRLwlBiyl1owWF5yGx4xnJ712p94Ws9gKZNg69ujYB1jIJ8k4hpk7xxmsGKNBqmLBi9OyOVTR6cVCGxVRirVii1fxi2cjaIakyCaFuFdV+UbUWXcEaXd1iAbmGHdWiIfHWRfW6VfHOkdkSifHnCPiPDWSDLbzmOfICKniqOri25ihS4tROnuzqFl1SKgm2NgnmMl26Xg2yXhXWUmGSWl3aNsU2Oo3GHsW2NuXKSo2eQrHOesn2pgVi7hUq1iVimh2eii3ulkn20jGG4mHepq3ukvGWtvXC0vHuVyjK5zhSoyTiSxEiKyHGD126H2XGU13eF5XGa5Hq3zUKvxG+i8H7HmRvViTLapCT9lRHskSfspy7IjEjDjVLMkk/Xk0XYnVnRnXHap2vgnVDtolHgpmHF0xrc0STY5CLi7CbF3EfP40yFhISGk4qInJOWiYObkomXl5eMoZeTp52mjYaoj5WploOmm5OzjYixnIe1mJmllaKvo4qqopq2o4y7qJK7uYWnpqa0q6Wyq7G7squ2tra3wben74GT//+t///CrJXEvY7HspnUoYXVsojQs5zMq6XJrbDOvKbGvbLRvaXEvcTSwarayLHhx6vszbHMyszO///8/f0AAADTgYy9AAABAHRSTlP///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////8AU/cHJQAAAAlwSFlzAAALEwAACxMBAJqcGAAAIjhJREFUeF7tfQ10G9d55cah1wwHscoJC8nYTWrXUriuSdBIp7RhoXtsq9latuIYOAoQqqzqxD2p1zq0o1qJSivrYEg6qRTXzmo5Frdpmkqg+7O05KS2kzBglKRNUydrQ6IgZcFFfAQsKDNdY7FhQkNQlhb3fu89ADPgAATIgS0KvBLxBvMD8bvvvu/nzcPoXy00ONYIEG3DYo0A0TYs1ggQbcNijQDRNizWCBBtw+JyIWB6alps1YjLgoCzqrJPUYLqlHhfCy4DAjRFUdyqqqIJamJf9bCMgJMd7e0dp8WbtxCaW1G0eCKdTsQ1cKCeFfurhUUEdMg2SZJlm22n2PEW4WwQ5qez2WwmM4uXWFAJTopDVcIaAmyyJEmgQLLJ14hdbwkmVcUdz85m8shmMB5qGwaWEADT13t9Pp8XPMgbFnbeckYcqDPUoKKmc8J4jmzMXRsDVhDQLsn+HTt6gIBPZgNBfktGQhD2o9ONyCWDSi3RwAoCJJvf7/DBfKLALtkI4lA9YWo/NJBWFXFGNbCAgA7J4ZWaJK93vcMPBmxNcAX1d4avkf3pxfaDAWhAnFQFVkzAznZonkyGCwQLgR6/12uT5DZxuF6Yhv3BUvvneJNNu1Vx2tJYIQEdNpnGvI1+AEkKBAI9O3zwheKEesHE/rlcNjvHOMgmlFPivCWxMgI2cLsLkOwYA6AAjkCcUScEkfMkjfaT9XN4oe1crOpBsCICTouOL0Cy+wLEgKPOBLyG/CdmjH9zOdhPFOSIgmyoWgZWREC7sFsHREREA3trfQlA0qsW0x8G6n8OJoLZakOB1QTADYABu9QuTqkP3O5FAigSwBjIZtTqHOGKCOiDuSzo6SE5evy2VnFGnaDCAwrLBYTtHIyBhFJVVbAiAm5ulb1eh83IgCT3OJqkuuYB00FFM44AvQCA7FwaSXFVGeFKCJCbbIh5O/LJ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"), false);
                TmxMapLoader tmxMapLoader = new TmxMapLoader(new LocalFileResolver());
                tmxMapLoader.getDependencies("", local, (BaseTmxMapLoader.Parameters) null);
                AssetManager assetManager = new AssetManager(new LocalFileResolver());
                assetManager.load("tileSet.png", Texture.class);
                assetManager.finishLoading();
                tmxMapLoader.loadAsync(assetManager, "map_flag.tmx", local, (TmxMapLoader.Parameters) null);
                this.map.dispose();
                this.map = tmxMapLoader.loadSync((AssetManager) null, (String) null, (FileHandle) null, (TmxMapLoader.Parameters) null);
                this.renderer = new OrthogonalTiledMapRenderer(this.map, 0.0625f);
            } catch (Exception e2) {
                e2.printStackTrace();
            }
        }
    }

```

Enough about what we should have done, onto what I actually did.

Looking at the function above, we can see an initial check that is being constructed based on the questionmark titles status, we need to trigger the condition `if (toHex(messageDigest.digest()).equals("024800ace2ec394e6af68baa46e81dfbea93f0f6730610560c66ee9748d91420")) {` and for that we need to find out the correct tile configuration.

First point is, can we bruteforce the code to find out what we need to know ignoring the game?

Usually the answer to this question would be no, too big of a searching space to bruteforce. However, in this scenario it would help us understanding how many different values can a tile have, maybe the search space is not that huge after all.

```Java
MessageDigest messageDigest;
int intValue;
byte[] bArr = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
TiledMapTileLayer tiledMapTileLayer = this.map.getLayers().get("questionmarks");
int i = 0;
int i2 = 0;
while (i < 100) {
    int i3 = i2;
    for (int i4 = 0; i4 < 100; i4++) {
        TiledMapTileLayer.Cell cell = tiledMapTileLayer.getCell(i, i4);
        if (!(cell == null || !cell.getTile().getProperties().containsKey("questionmarkType") || (intValue = ((Integer) cell.getTile().getProperties().get("questionmarkType")).intValue()) == 1337)) {
            bArr[i3] = (byte) intValue;
            i3++;
        }
    }
    i++;
    i2 = i3;
}
try {
    messageDigest = MessageDigest.getInstance("SHA-256");
} catch (NoSuchAlgorithmException e) {
    e.printStackTrace();
    messageDigest = null;
}
messageDigest.update(bArr);
messageDigest.update("P4ssw0rdS4lt".getBytes());
if (toHex(messageDigest.digest()).equals("024800ace2ec394e6af68baa46e81dfbea93f0f6730610560c66ee9748d91420")) {
```

The answer to the above question is, we have 4 status only, we saw this on the code of the `update_koala` method, we could also double check this from the config files found on the directory `assets`, the `map.tmx`.

```Java
 if (cell2.getTile().getProperties().containsKey("questionmarkType")) {
    int intValue = ((Integer) cell2.getTile().getProperties().get("questionmarkType")).intValue();
    if (intValue == 1337) {
        new Array();
        checkFlag();
    } else {
        if (intValue == 0) {
            intValue = 21;
        } else if (intValue == 21) {
            intValue = 97;
        } else if (intValue == 97) {
            intValue = 37;
        } else if (intValue == 37) {
            intValue = 0;
        }
        try {
            new TiledMapTileLayer.Cell();
            cell2.setTile(this.map.getTileSets().getTile(this.questionMarkTileMapping.get(Integer.valueOf(intValue)).intValue()));
            tiledMapTileLayer.setCell((int) rectangle2.x, (int) rectangle2.y, cell2);
        } catch (Exception unused) {
        }
    }
    z = true;
}
```
I'm couting 4 as the 1337 is what trigger the `check_flag` method and it's being ignored on the code.

```xml
<tileset firstgid="1" name="tileSet" tilewidth="16" tileheight="16" tilecount="256" columns="16">
  <image source="tileSet.png" width="256" height="256"/>
  <tile id="127">
   <properties>
    <property name="questionmarkType" type="int" value="0"/>
   </properties>
  </tile>
  <tile id="159">
   <properties>
    <property name="questionmarkType" type="int" value="21"/>
   </properties>
  </tile>
  <tile id="175">
   <properties>
    <property name="questionmarkType" type="int" value="37"/>
   </properties>
  </tile>
  <tile id="191">
   <properties>
    <property name="questionmarkType" type="int" value="97"/>
   </properties>
  </tile>
  <tile id="207">
   <properties>
    <property name="questionmarkType" type="int" value="1337"/>
   </properties>
  </tile>
 </tileset>
```


With this info we can do a dumb bruteforce on each byte array position until we crack the code.

So, phase 1, crack the byte sequence:

```Java
MessageDigest messageDigest;
String str3 = "RC4";
byte[] bArr = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};

int[] possibleValues = new int[] {0 , 21, 37, 97}; 

for(int i1 = 0; i1 < 4; i1 ++) {
    for(int i2 = 0; i2 < 4; i2 ++) {
        for(int i3 = 0; i3 < 4; i3 ++) {
            for(int i4 = 0; i4 < 4; i4 ++) {
                for(int i5 = 0; i5 < 4; i5 ++) {
                    for(int i6 = 0; i6 < 4; i6 ++) {
                        for(int i7 = 0; i7 < 4; i7 ++) {
                            for(int i8 = 0; i8 < 4; i8 ++) {
                                for(int i9 = 0; i9 < 4; i9 ++) {
                                    for(int i10 = 0; i10 < 4; i10 ++) {
                                        for(int i11 = 0; i11 < 4; i11 ++) {
                                    
                                            bArr[0] = (byte) possibleValues[i1];
                                            bArr[1] = (byte) possibleValues[i2];
                                            bArr[2] = (byte) possibleValues[i3];
                                            bArr[3] = (byte) possibleValues[i4];
                                            bArr[4] = (byte) possibleValues[i5];
                                            bArr[5] = (byte) possibleValues[i6];
                                            bArr[6] = (byte) possibleValues[i7];
                                            bArr[7] = (byte) possibleValues[i8];
                                            bArr[8] = (byte) possibleValues[i9];
                                            bArr[9] = (byte) possibleValues[i10];
                                            bArr[10] = (byte) possibleValues[i11];
                                            
                                            try {
                                                messageDigest = MessageDigest.getInstance("SHA-256");
                                            } catch (NoSuchAlgorithmException e) {
                                                e.printStackTrace();
                                                messageDigest = null;
                                            }
                                            messageDigest.update(bArr);
                                            String str5 = "P4ssw0rdS4lt";
                                            messageDigest.update(str5.getBytes());
                                            
                                            if( toHex(messageDigest.digest()).equals("024800ace2ec394e6af68baa46e81dfbea93f0f6730610560c66ee9748d91420")) {
                                                System.out.println("FOUND");
                                                System.out.println(bArr);
                                            }
                                            
                                            
                                        }
                                    }
                                }

                            }	
                        }	
                    }	
                }	
            }	
        }	
    }	
}
```

Result was found in couple seconds, despite the scary sequence of embeeded for loops: `byte[] bArr = new byte[] {21, 0, 97, 37, 21, 37, 37, 97, 97, 37, 21};`

Now, onto the next phase, let's get that final map, the rest of the code is expecting an ecrypted file (the map that is encrypted) to be decrypted by using our `messageDigest`, as we don't need to change absolutely nothing I just made sure to make the resources available for the code to proceed until I get the final map file.

```Java
private static void checkFlag() {
MessageDigest messageDigest;
//String str = "tileSet.png";
//String str2 = "map_flag.tmx";
String str3 = "RC4";
byte[] bArr = new byte[] {21, 0, 97, 37, 21, 37, 37, 97, 97, 37, 21};

try {
    messageDigest = MessageDigest.getInstance("SHA-256");
} catch (NoSuchAlgorithmException e) {
    e.printStackTrace();
    messageDigest = null;
}
messageDigest.update(bArr);
String str5 = "P4ssw0rdS4lt";
messageDigest.update(str5.getBytes());

if (toHex(messageDigest.digest()).equals("024800ace2ec394e6af68baa46e81dfbea93f0f6730610560c66ee9748d91420")) {
    try {
        messageDigest.update(bArr);
        messageDigest.update(str5.getBytes());
        messageDigest.update(bArr);
        byte[] digest = messageDigest.digest();
        
        File file=new File("C:\\Users\\blu3drag0nsec\\eclipse-workspace\\alles\\src\\alles\\flag_enc");    //creates a new file instance  
        FileReader fr=new FileReader(file);   //reads the file  
        BufferedReader br=new BufferedReader(fr);  //creates a buffering character input stream  
        StringBuffer sb=new StringBuffer();    //constructs a string buffer with no characters  
        String line;  
        while((line=br.readLine())!=null)  
        {  
            sb.append(line);      //appends line to string buffer
        }  
        fr.close();    //closes the stream and release the resources
        
        String flag_enc = sb.toString();
                
        byte[] decode = Base64Coder.decode(flag_enc );
        SecretKeySpec secretKeySpec = new SecretKeySpec(digest, 0, digest.length, str3);
        Cipher instance = Cipher.getInstance(str3);
        instance.init(2, secretKeySpec, instance.getParameters());
        String str6 = new String(instance.doFinal(decode));
                        
        FileWriter myWriter = new FileWriter("C:\\Users\\blu3drag0nsec\\eclipse-workspace\\alles\\src\\alles\\map_flag.tmx");
        myWriter.write(str6);
        myWriter.close();
        
        
    } catch (Exception e2) {
        e2.printStackTrace();
    }
}
}
```

The file was saved to `map_flag.tmx` and remember, lazy approach, so what immediatly jumps to mind is, can we edit this map file format?

Apparently the answer was a simple `yes`, this is a known format, literally the first google result: https://www.mapeditor.org/

After installing the map and opening the newly generated file, we got the flag (in a very odd format but still).

![image](https://user-images.githubusercontent.com/69213271/92546458-9885c400-f220-11ea-8427-6ea0b9a7cbe1.png)

Flag: `ALLES{1TS_A_DINO}`
