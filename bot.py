import sys
import time
import telepot
import Queue

# TODO: usare un database magari
voice_queue = Queue.Queue()
user_count = dict()

if len(sys.argv) >= 2:
    TOKEN = sys.argv[1]
else:
    try:
        f = open('token', 'rb')
        TOKEN = f.read().strip()
        f.close()
    except IOError:
        print 'Crea un file token o passa la token come argomento.'
        sys.exit()



print '===============', TOKEN
def handle(msg):
    flavor = telepot.flavor(msg)
    summary = telepot.glance(msg, flavor=flavor)

    print "Richiesta da ", msg['from']['id']

    if flavor == 'chat' and 'voice' in msg:
        save_voice(msg)
        send_voice(msg)
    else:
        bot.sendMessage(msg['chat']['id'], 'NONONO solo messaggi vocali per ora')

    print "Dimensione della coda: ", voice_queue.qsize()
        
def save_voice(msg):
    #voice_queue.put(msg['voice']['file_id'])
    print "\tsalvo messaggio vocale da ", msg['from']['id']
    voice_queue.put_nowait(msg)
    user_id = msg['from']['id']

    #Inizializza o incrementa il numero di messaggi mandati da user_id
    if user_id in user_count:
        user_count[user_id] += 1
        print '\tincremento count di ', user_id,  user_count[user_id]
    else:
        user_count[user_id] = 1
        print '\tinizializzo count di ', user_id

#si assume sempre che ci sia almeno un messaggio, e questo non va bene
def send_voice(msg):
    current_user = msg['from']['id']
    voice_msg = voice_queue.get_nowait()

    print "\tinvio messaggio vocale a ", msg['from']['id']
    print "\t\tprendo dalla coda il messaggio di ", voice_msg['from']['id']
    
    # qui si assume sempre che user_count[current_user] esista..
    count = 0
    while voice_msg['from']['id'] == current_user and count < user_count[current_user]:
        count += 1
        voice_queue.put_nowait(voice_msg)
        voice_msg = voice_queue.get_nowait()
        print "\t\tprendo dalla coda il messaggio di ", voice_msg['from']['id']

    if count == user_count[current_user]:
        bot.sendMessage(msg['chat']['id'], "Ancora non ci sono messaggi per te. Riprova piu tardi")
        voice_queue.put(voice_msg)
    else:
        "\t\tprocedo a inviare il messaggio di ",voice_msg['from']['id'], " a ", current_user
        bot.sendVoice(msg['chat']['id'], voice_msg['voice']['file_id'])
        user_count[voice_msg['from']['id']] -= 1

    # TODO: trovare un metodo migliore per evitare che non si rimanga senza messaggi vocali
    # soprattutto in fase di inizializzazione

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print 'Listening ...'

# Keep the program running.
while 1:
    time.sleep(10)
