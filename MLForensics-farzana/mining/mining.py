import os
import pandas as pd 
import numpy as np
import csv 
import time 
from datetime import datetime
import subprocess
import shutil
from git import Repo, exc 
import logging
logger = logging.getLogger(__name__)
log_filename = f"mining_forensics.log"
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(funcName)-20s | %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        #logging.StreamHandler()  #also log to console
    ]
)
def giveTimeStamp():
  tsObj = time.time()
  strToret = datetime.fromtimestamp(tsObj).strftime('%Y-%m-%d %H:%M:%S')
  return strToret
  

def deleteRepo(dirName, type_):
    print(':::' + type_ + ':::Deleting ', dirName)
    try:
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
    except OSError:
        print('Failed deleting, will try manually')  
        
# Method for fuzzing/logging     
def dumpContentIntoFile(strP, fileP):
    logger.info("=" * 80)
    logger.info("dumpContentIntoFile ENTRY | content_type=%s content_len=%s | path_type=%s path=%s",
                type(strP).__name__, len(str(strP)), type(fileP).__name__, repr(fileP)[:50])
    
    try:
        fileToWrite = open(fileP, 'w')
        fileToWrite.write(str(strP))
        fileToWrite.close()
        
        size = os.stat(fileP).st_size
        logger.info("dumpContentIntoFile EXIT | bytes_written=%d", size)
        logger.info("=" * 80)
        return str(size)
    except Exception as e:
        logger.error("dumpContentIntoFile CRASHED | error_type=%s | error=%s", type(e).__name__, str(e))
        logger.info("=" * 80)
        raise
  
# Method for fuzzing/logging
def makeChunks(the_list, size_):
    logger.info("=" * 80)
    logger.info("makeChunks ENTRY | list_len=%s list_type=%s | size=%s size_type=%s", 
                len(the_list), type(the_list).__name__, repr(size_), type(size_).__name__)
    
    try:
        chunk_count = (len(the_list) + size_ - 1) // size_
        logger.info("makeChunks: expected_chunks=%s", chunk_count)
        
        actual_chunks = 0
        for i in range(0, len(the_list), size_):
            chunk = the_list[i:i+size_]
            actual_chunks += 1
            logger.debug("makeChunks: chunk#%d | range=[%d:%s] | size=%d", actual_chunks, i, i+size_, len(chunk))
            yield chunk
        
        logger.info("makeChunks EXIT | chunks_yielded=%d", actual_chunks)
        logger.info("=" * 80)
    except Exception as e:
        logger.error("makeChunks CRASHED | error_type=%s | error=%s", type(e).__name__, str(e))
        logger.info("=" * 80)
        raise
        
def cloneRepo(repo_name, target_dir):
    cmd_ = "git clone " + repo_name + " " + target_dir 
    try:
       subprocess.check_output(['bash','-c', cmd_])    
    except subprocess.CalledProcessError:
       print('Skipping this repo ... trouble cloning repo:', repo_name )

# Method for fuzzing/logging
def checkPythonFile(path2dir):
    logger.info("=" * 80)
    logger.info("checkPythonFile ENTRY | path_type=%s path=%s",
                type(path2dir).__name__, repr(path2dir)[:50])
    
    try:
        usageCount = 0
        files_processed = 0
        patternDict = ['sklearn', 'h5py', 'gym', 'rl', 'tensorflow', 'keras', 'tf', 
                       'stable_baselines', 'tensorforce', 'rl_coach', 'pyqlearning', 
                       'MAMEToolkit', 'chainer', 'torch', 'chainerrl']
        
        for root_, dirnames, filenames in os.walk(path2dir):
            for file_ in filenames:
                full_path_file = os.path.join(root_, file_)
                
                if os.path.exists(full_path_file):
                    if (file_.endswith('py')) or (file_.endswith('ipynb')):
                        files_processed += 1
                        logger.debug("checkPythonFile: processing file#%d | %s", files_processed, file_)
                        
                        f = open(full_path_file, 'r', encoding='latin-1')
                        pythonFileContent = f.read()
                        pythonFileContent = pythonFileContent.split('\n')
                        pythonFileContent = [z_.lower() for z_ in pythonFileContent if z_ != '\n']
                        
                        for content_ in pythonFileContent:
                            for item_ in patternDict:
                                if item_ in content_:
                                    usageCount += 1
                                    logger.debug("checkPythonFile: match#%d | pattern=%s", usageCount, item_)
        
        logger.info("checkPythonFile EXIT | files_processed=%d | total_matches=%d", files_processed, usageCount)
        logger.info("=" * 80)
        return usageCount
    except Exception as e:
        logger.error("checkPythonFile CRASHED | error_type=%s | error=%s", type(e).__name__, str(e))
        logger.info("=" * 80)
        raise
    
# Method for fuzzing/logging
def days_between(d1_, d2_): ## pass in date time objects, if string see commented code 
    # d1_ = datetime.strptime(d1_, "%Y-%m-%d")
    # d2_ = datetime.strptime(d2_, "%Y-%m-%d")
    logger.info("=" * 80)
    logger.info("days_between ENTRY | d1_type=%s d1=%s | d2_type=%s d2=%s",
                type(d1_).__name__, str(d1_), type(d2_).__name__, str(d2_))
    
    try:
        days_between = abs((d2_ - d1_).days)
        
        logger.info("days_between EXIT | result=%d", days_between)
        logger.info("=" * 80)
        return days_between
    except Exception as e:
        logger.error("days_between CRASHED | error_type=%s | error=%s", type(e).__name__, str(e))
        logger.info("=" * 80)
        raise
    
def getDevEmailForCommit(repo_path_param, hash_):
    author_emails = []

    cdCommand         = "cd " + repo_path_param + " ; "
    commitCountCmd    = " git log --format='%ae'" + hash_ + "^!"
    command2Run = cdCommand + commitCountCmd

    author_emails = str(subprocess.check_output(['bash','-c', command2Run]))
    author_emails = author_emails.split('\n')
    # print(type(author_emails)) 
    author_emails = [x_.replace(hash_, '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('^', '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('!', '') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    author_emails = [x_.replace('\\n', ',') for x_ in author_emails if x_ != '\n' and '@' in x_ ] 
    try:
        author_emails = author_emails[0].split(',')
        author_emails = [x_ for x_ in author_emails if len(x_) > 3 ] 
        # print(author_emails) 
        author_emails = list(np.unique(author_emails) )
    except IndexError as e_:
        pass
    return author_emails  
    
def getDevDayCount(full_path_to_repo, branchName='master', explore=1000):
    repo_emails = []
    all_commits = []
    repo_emails = []
    all_time_list = []
    if os.path.exists(full_path_to_repo):
        repo_  = Repo(full_path_to_repo)
        try:
           all_commits = list(repo_.iter_commits(branchName))   
        except exc.GitCommandError:
           print('Skipping this repo ... due to branch name problem', full_path_to_repo )
        # only check commit by commit if less than explore threshold

        for commit_ in all_commits:
            commit_hash = commit_.hexsha

            emails = getDevEmailForCommit(full_path_to_repo, commit_hash)
            repo_emails = repo_emails + emails
            
            timestamp_commit = commit_.committed_datetime
            str_time_commit  = timestamp_commit.strftime('%Y-%m-%d') ## date with time 
            all_time_list.append( str_time_commit )

    all_day_list   = [datetime(int(x_.split('-')[0]), int(x_.split('-')[1]), int(x_.split('-')[2]), 12, 30) for x_ in all_time_list]
    try:
        min_day        = min(all_day_list) 
        max_day        = max(all_day_list) 
        ds_life_days   = days_between(min_day, max_day)
    except (ValueError, TypeError):
        ds_life_days   = 0
    ds_life_months = round(float(ds_life_days)/float(30), 5)
    
    return len(repo_emails) , len(all_commits) , ds_life_days, ds_life_months 
            
# Method for fuzzing/logging
def getPythonFileCount(path2dir):
    logger.info("=" * 80)
    logger.info("getPythonFileCount ENTRY | path_type=%s path=%s",
                type(path2dir).__name__, repr(path2dir)[:50])
    
    try:
        valid_list = []
        for root_, dirnames, filenames in os.walk(path2dir):
            for file_ in filenames:
                if (file_.endswith('py')) or (file_.endswith('ipynb')):
                    valid_list.append(file_)
                    logger.debug("getPythonFileCount: found file#%d | %s", len(valid_list), file_)
        
        logger.info("getPythonFileCount EXIT | python_files=%d", len(valid_list))
        logger.info("=" * 80)
        return len(valid_list)
    except Exception as e:
        logger.error("getPythonFileCount CRASHED | error_type=%s | error=%s", type(e).__name__, str(e))
        logger.info("=" * 80)
        raise
    
    

def cloneRepos(repo_list, dev_threshold=3, python_threshold=0.10, commit_threshold = 25): 
    counter = 0     
    str_ = ''
    all_list = []
    for repo_batch in repo_list:
        for repo_ in repo_batch:
            counter += 1 
            print('Cloning ', repo_ )
            dirName = '../FSE2021_REPOS/' + repo_.split('/')[-2] + '@' + repo_.split('/')[-1] ## '/' at the end messes up the index 
            cloneRepo(repo_, dirName )
            ### get all count 
            checkPattern, dev_count, python_count, commit_count, age_months   = 0 , 0, 0, 0, 0 
            flag = True
            all_fil_cnt = sum([len(files) for r_, d_, files in os.walk(dirName)])
            python_count = getPythonFileCount(dirName) 
            if (all_fil_cnt <= 0):
                deleteRepo(dirName, 'NO_FILES')
                flag = False
            elif (python_count < (all_fil_cnt * python_threshold) ):
                deleteRepo(dirName, 'NOT_ENOUGH_PYTHON_FILES')
                flag = False
            else:       
                dev_count, commit_count, age_days, age_months  = getDevDayCount(dirName)
                if (dev_count < dev_threshold):                
                    deleteRepo(dirName, 'LIMITED_DEVS') 
                    flag = False  
                elif (commit_count < commit_threshold):                
                    deleteRepo(dirName, 'LIMITED_COMMITS')  
                    flag = False
            if (flag == True ): 
                checkPattern = checkPythonFile(dirName) 
                if (checkPattern == 0 ):
                    deleteRepo(dirName, 'NO_PATTERN')
                    flag = False        
            print('#'*100 )
            str_ = str_ + str(counter) + ',' +  repo_ + ',' + dirName + ','  + str(checkPattern) + ',' + str(dev_count) + ',' + str(flag) + ',' + '\n'
            tup = ( counter,  dirName, dev_count, all_fil_cnt, python_count , commit_count, age_months, flag)
            all_list.append( tup ) 
            print("So far we have processed {} repos".format(counter) )
            if((counter % 100) == 0):
                dumpContentIntoFile(str_, 'tracker_completed_repos.csv')
                df_ = pd.DataFrame( all_list ) 
                df_.to_csv('PYTHON_BREAKDOWN.csv', header=['INDEX', 'REPO', 'DEVS', 'FILES', 'PYTHON_FILES', 'COMMITS', 'AGE_MONTHS', 'FLAG'] , index=False, encoding='utf-8')    

            if((counter % 1000) == 0):
                print(str_)                
            print('#'*100)
        print('*'*10)
        
   

if __name__=='__main__':
    repos_df = pd.read_csv('PARTIAL_REMAINING_GITHUB.csv', sep='delimiter')
    print(repos_df.head())
    list_    = repos_df['url'].tolist()
    list_ = np.unique(list_)
    
    t1 = time.time()
    print('Started at:', giveTimeStamp() )
    print('*'*100 )

    
    print('Repos to download:', len(list_)) 
    ## need to create chunks as too many repos 
    chunked_list = list(makeChunks(list_, 100))  ### list of lists, at each batch download 1000 repos 
    cloneRepos(chunked_list)


    print('*'*100 )
    print('Ended at:', giveTimeStamp() )
    print('*'*100 )
    t2 = time.time()
    time_diff = round( (t2 - t1 ) / 60, 5) 
    print('Duration: {} minutes'.format(time_diff) )
    print( '*'*100  )  
