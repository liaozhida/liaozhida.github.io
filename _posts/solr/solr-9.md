tokenizer的作用是将输入的文本切成一个个词元token,一些字符可能被丢弃也可能被替换，比如空格和标点符号会被丢弃。一个词元除了本身的值以外还包含了各样的元数据，例如词元在该字段出现的位置，因为分词器产生的词元可能和输入的文本不一样，你不能假定词元的值和该字段的原始值一样，或者词元的长度和原来的文本长度一致(比如原来该字段的文本是cars，但是分词处理过后可能为car);另外不止一个词元拥有相同的Position位置信息，比如"中华人民共和国"，分词处理之后‘人民’词元和‘人民共和国’词元就是位于该原文本值相同的Position，当我们使用词元元数据的时候一定要牢记这一点。

#####可以在analyzer结点中配置tokenizer#####

作为analyzer的子节点，如下所示，class属性的factory类会实例化出需要的tokenizer实例，TokenizerFactory 继承至==org.apache.solr.analysis.TokenizerFactory==,TokenizerFactory创建出的tokenizer实例必须继承自==org.apache.lucene.analysis.TokenStream==;TokenizerFactory的create方法接收一个reader参数并返回一个TokenStream，当solr创建一个tokenizer的时候,会向它传进去一个包含字段field内容的reader参数，tokenizer产生的词元token将为下一阶段的filter过滤器所使用。

TypeTokenFilterFactory可以创建出TypeTokenFilter，然后基于他们的TypeAttribute去过滤词元，TypeAttribute在factory.getStopTypes中设置，例子：
```Markup
<fieldType name="text" class="solr.TextField">  
  <analyzer type="index">
    <tokenizer class="solr.StandardTokenizerFactory"/>
    <filter class="solr.StandardFilterFactory"/>
  </analyzer>
</fieldType>
```


#####下面介绍官方给出的一些tokenizer StandardTokenizer #####

######Factory class: solr.StandardTokenizerFactory ######
参数:maxTokenLength token词元的最大长度 默认是255 去除空格和标点符号，带连字符的将被分成两个词元 x-art分成x和art,@符号也会被过滤
```Markup
Input:  "Please, email john.doe@foo.com by 03-09, re: m37-xq."
Output: "Please", "email", "john.doe", "foo.com", "by", "03", "09", "re", "m37", "xq"ClassicTokenizerFactory
```

######Factory class: solr.ClassicTokenizerFactory ######
参数:maxTokenLength token词元的最大长度 默认是255 表现行为和StandardTokenizer相似，区别：带连字符文本中，如果存在数字不会拆分；能够识别互联网域名和email地址 
```Markup
Input:  "Please, email john.doe@foo.com by 03-09, re: m37-xq."
Output:  "Please", "email", "john.doe@foo.com", "by", "03-09", "re", "m37-xq"KeywordTokenizerFactory
```

######Factory class: solr.KeywordTokenizerFactory ######
把整个文本当做一个词元 
```Markup
Input:  "Please, email john.doe@foo.com by 03-09, re: m37-xq." 
Output:  "Please, email john.doe@foo.com by 03-09, re: m37-xq."LetterTokenizerFactory
```

######Factory class: solr.LetterTokenizerFactory ######
丢弃所有非文字字符 
```Markup
Input:  "I can’t." 
Output:  "I", "can", "t"
```

######LowerCaseTokenizerFactory Factory class: solr.LowerCaseTokenizerFactory ######
丢弃所有非文字字符，过滤空格还有标点符号，将所有大写字母转成小写 
```Markup
Input:  "I Can’t. Please" 
Output:  "I", "can", "t","please"
```

######NGramTokenizerFactory ######
######Factory class: solr.NGramTokenizerFactory ######
读取字段然后在给定的范围内生成多个token，看例子很容易理解 参数： minGramSize：最小切割值，默认为1 
maxGramSize:词元最大长度，默认为2 
1.minGramSize:2 maxGramSize:3 
```Markup
Input: abcde 
Output: ab abc abc bc bcd cd cde
```
2.minGramSize:2 maxGramSize:5 
```Markup
Input:  abcde 
Output:： ab abc abcd abcde bc bcd bcde cd cde deEdgeNGramTokenizerFactory
```

######Factory class: solr.EdgeNGramTokenizerFactory ######
参数 minGramSize：同上 maxGramSize：同上 
side：从文本哪一边开始分析 
Edge n-gram range of 2 to 5 
```Markup
Input:  "babaloo" 
Output: "ba", "bab", "baba", "babal"PathHierarchyTokenizerFactory
```

######Factory class: solr.PathHierarchyTokenizerFactory ######
使用新的文件目录符去代替文本中的目录符 
参数：delimiter：文本的目录符 replace：替代目录符 
```Markup
Input:  "c:\usr\local\apache" 
Output:  "c:", "c:/usr", "c:/usr/local", "c:/usr/local/apache"PatternTokenizerFactory
```

######Factory class: solr.PatternTokenizerFactory ######
参数：  pattern：正则表达式，语义和java.util.regex.Pattern.一致 ;group：与java.util.regex的group语义相同 
pattern="[A-Z][A-Za-z]*" group="0″ 
```Markup
Input:  "Hello. My name is Inigo Montoya. You killed my father. Prepare to die." 
Output:  "Hello", "My", "Inigo", "Montoya", "You", "Prepare"
```

######UAX29URLEmailTokenizerFactory ######
参数：maxTokenLength:默认255 最大词元长度 去除空格和标点符号，但是保留url和email的链接 
```Markup
Input:  "Visit http://accarol.com/contact.htm?from=external&a=10 or e-mail bob.cratchet@accarol.com" 
Output:  "Visit", "http://accarol.com/contact.htm?from=external&a=10", "or", "e", "mail", "bob.cratchet@accarol.com"WhitespaceTokenizerFactory
````
只是去除空格，标点符号是保存下来的 
```Markup
Input:  "To be, or what?" 
Output:  "To", "be,", "or", "what?"
```


