# Uitgooi
This script was explicitly written for job I currently work at, it's use outside of this job would be extreamly limited.

The main idea is that it coppies images from a given directory into a file structure specified in a JSON file.

The JSON file specifies the meaning of A, B, C, etc. It can contain multiple such discriptions that the user can choose from.

```
{

  'Name of structure 1':
  {
    'A-SomeText':'E',
    'B-SomeText':
    {
        'A-SomeText':'E'
    },
    'C-SomeText':
    {
        'A-SomeText':'E',
        'D-SomeText':'E'
    },
    'D-SomeText':'E',
    .
    .
    .
  }

  'Name of structure 2':
   {
      .
      .
      .
   }
}
```

The files that need to be coppied are given in a CSV file in the format
```
1234,A
2342,B
1232,C
2242,D
2242,D
.
.
.
```

The script indexes a source directory which contains images with a file name in the format `ER-1234.jpg`

The result of the program would be a file tree that looks something like this if structure 1 was chosen.
```
A-SomeText
  ER-1234.jpg

B-SomeText
  A-SomeText
    ER-2342.jpg

C-SomeText
  A-SomeText
    ER-1232.jpg
  D-SomeText
    ER-1232.jpg

D-SomeText
  ER-2242.jpg
  ER-2242 (2).jpg
  
```

The script has a GUI made with PyQt6. 

Along with it's main functionality it has allot of extra checks and safty mesures in place to support the process it was meant to automate.

