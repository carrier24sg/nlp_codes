import traceback
import pdb
""" answer to the programming assignment 1 from coursera nlp class from Columbia University """
def replace_counts(input_filename, op_filename):
    f = open(input_filename, 'rb')
    f2 = open(op_filename, 'w')
    for line in f:
        print 'line is %s' %line 
        split_line = line.split(' ')
        count = int(split_line[0])
        if count < 5 and split_line[1] == "WORDTAG":
            split_line[3] = "_RARE_\n"
        new_str = ' '.join(split_line)
        f2.write("%s" %new_str)

    f.close()
    f2.close()

class Baseline_tagger:
    def __init__(self, counts_file):
        self.tag_counts = {}
        self.word_counts = {}
        self.seq_counts = {}
        f = open(counts_file, 'rb')
        for line in f:
            try:
                split_line = line.split(' ')
                if split_line[1] == 'WORDTAG':
                    tag = split_line[2].strip()
                    word = split_line[3].strip()
                    if tag in self.tag_counts:
                        self.tag_counts[tag] += int(split_line[0])
                    else:
                        self.tag_counts[tag] = int(split_line[0])
                    if word in self.word_counts:
                        if tag in self.word_counts[word]:
                            self.word_counts[word][tag] += int(split_line[0])
                        else:
                            self.word_counts[word][tag] = int(split_line[0])
                    else:
                        self.word_counts[word] = {tag: int(split_line[0])}

                elif split_line[1] == '2-GRAM':
                    self.seq_counts[(split_line[2].strip(), split_line[3].strip())]  = int(split_line[0])
                elif split_line[1] == '3-GRAM':
                    self.seq_counts[(split_line[2].strip(),split_line[3].strip(), split_line[4].strip())] = int(split_line[0])
            except:
                traceback.print_exc()
                print 'offending line is %s' %(line)
        f.close()

    def determine_tag(self, word):
        if word not in self.word_counts:
            word = "_RARE_"
        max_prob = -1
        return_tag = None
        for d in self.word_counts[word]:
            for tag, word_count in self.word_counts[word].items():
                score = float(word_count) / self.tag_counts[tag]
                if score > max_prob:
                    max_prob = score
                    return_tag = tag
        return return_tag

    def run(self, test_file, output_file):
        f = open(output_file, 'w')
        for word in open(test_file):
            if word == "\n":
                f.write("\n")
                continue
            word = word.strip()
            f.write("%s %s\n"%(word, self.determine_tag(word)))
        f.close()
        
class TrigramTagger(Baseline_tagger):
    def run(self, test_file, output_file):
        f = open(output_file, 'w')
        sentence = []
        
        for word in open(test_file):
            if word == '\n':
                tags = self.process_sentence(sentence)
                for i in xrange(len(sentence)):
                    f.write("%s %s\n" %(sentence[i], tags[i]) )
                f.write("\n")
                sentence = []
            else:
                sentence.append(word.strip())
        #for x in range(len(words)):
        #    if words[x] == '\n':
        #        space_counter += 1
        #        f.write(words[x])
        #        continue
        #    f.write("%s %s\n" %(words[x], final_tags[x-space_counter]))

        f.close()

    def process_sentence(self, sentence):
        all_tags = self.tag_counts.keys()
        k = 1
        pi = {'*':{'*':1}} #pi is a mapping of u : w
        backpointer = []

        for word in sentence:
            new_pi = {}
            bp_entry = {}
            for tag2 in all_tags:
                if len(pi) == 1:
                    tags1 = ['*']
                else:
                    tags1 = all_tags
                
                new_pi[tag2] = {} 

                for tag1 in tags1:
                    max_prob = -1
                    w_tag =  ''
                    for tag0, previous_pi in pi[tag1].items():
                        markov_score = self.seq_counts[(tag0, tag1, tag2)] / float(self.seq_counts[(tag0, tag1)])
                        if word not in self.word_counts:
                            word = "_RARE_"
                        score = previous_pi * markov_score *  (self.word_counts[word].get(tag2, 0)  / float(self.tag_counts[tag2]))
                        print 'score is %s' %score
                        if score > max_prob:
                            max_prob = score
                            w_tag = tag0
                    new_pi[tag2][tag1] = max_prob 
                    bp_entry[(tag1, tag2)] = w_tag
            if k > 2:
                backpointer.append(bp_entry)
            pi = new_pi
            k += 1

        final_tags = self.retrieve_sequence(backpointer, pi)
        return final_tags

    def retrieve_sequence(self, backpointers, pi):
        fscore = -1
        for tag2, dic in pi.items():
            for tag1, score in dic.items():
                score *= self.seq_counts[(tag1, tag2, 'STOP')] / float(self.seq_counts[(tag1, tag2)])
                if score > fscore:
                    fscore = score
                    final_tag2 =  tag2
                    final_tag1 =  tag1
        
        final_tags = [final_tag1, final_tag2, 'STOP']
        for x in reversed(range(len(backpointers))):
            w = backpointers[x][(final_tag1, final_tag2)]
            final_tags.insert(0, w)
            final_tag2 = final_tag1
            final_tag1 = w

        return final_tags



        


