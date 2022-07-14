from importlib.util import find_spec
from multiprocessing import context
from django.shortcuts import redirect, render
from .forms import *
from django.contrib import messages
from django.views import generic
from youtubesearchpython import VideosSearch
import requests
import wikipedia


# Create your views here.
def home(request):
    return render(request,'dashboard/home.html')

def notes(request):
    if( request.method == "POST"):
        form = NotesForm(request.POST)
        if form.is_valid() :
            notes = Notes(user = request.user, title = request.POST['title'], description = request.POST['description'])
            notes.save()
            messages.success(request,f"Notes are created successfully for {request.user.username}")

    else :
        form = NotesForm()
    notes = Notes.objects.filter(user = request.user)
    context = {'notes':notes, 'form':form}

    return render(request,'dashboard/notes.html',context)


def delete_note(request,pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect("notes")

class NoteDetails(generic.DetailView):
    model = Notes




def homework(request):
    
    
    if( request.method == "POST"):
        form = HomeworkForm(request.POST)
        if form.is_valid() :
            try:
                finished = request.POST['is_finished']
                if finished == "on":
                    finished = True
                else :
                    finished = False
            except:
                finished = False
            homework = Homework(user = request.user, 
            subject = request.POST['subject'], 
            title = request.POST['title'], 
            description = request.POST['description'], 
            due = request.POST['due'],
            is_finished = finished
            )
            

            homework.save()
            messages.success(request,f"Homework are created successfully for {request.user.username}")

    else :
        form = HomeworkForm()
    homeworks = Homework.objects.filter(user = request.user)
    if( len(homeworks) == 0):
        homework_done = True
    else :
        homework_done = False
    context = {'homeworks':homeworks, 'homework_done':homework_done,'form':form}
    return render(request,'dashboard/homework.html',context)


def update_homework(requset,pk):
    homework = Homework.objects.get(id = pk)
    if homework.is_finished == True :
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')
    
def delete_homework(request,pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect("homework")


#youtube

def youtube(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        video = VideosSearch(text,limit=10)
        result_list = []
        for i in video.result()['result']:  
            result_dir = {
                'input' : text,
                'title' : i['title'],
                'channel' : i['channel']['name'],
                'duration' : i['duration'],
                'thumbnail' : i['thumbnails'][0]['url'],
                'views' : i['viewCount']['short'],
                'link' : i['link'],
                'published':i['publishedTime']
            }

            desc = ''
            for j in i['descriptionSnippet']:
                desc += j['text']
            
            result_dir['description'] = desc
            result_list.append(result_dir)
        context = {'form':form, 'results': result_list}
        return render(request,'dashboard/youtube.html',context)
        
    else :
        form = DashboardForm()
    context = {'form':form}
    return render(request,"dashboard/youtube.html",context)


#ToDo

def todo(request):
    if request.method == "POST":
        form = Todoform(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if(finished == "on"):
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            todos = Todo(user = request.user, title = request.POST['title'],is_finished = finished)
            todos.save()
        messages.success(request,f"Item is added to ToDo list for {request.user.username}")

    else :
        form = Todoform()
    todos = Todo.objects.filter(user = request.user)
    context = {'todos':todos,'form':form}
    return render(request,'dashboard/todo.html',context)

def upadte_todo(request,pk):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True

    todo.save()
    return redirect('todo')

def delete_todo(request,pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('todo')


#Book

def books(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://www.googleapis.com/books/v1/volumes?q=" + text
        r = requests.get(url)
        answer = r.json()
        result_list = []
        for i in range(10):  
            thumb = answer['items'][i]['volumeInfo'].get('imageLinks')
            if thumb :
                thumb = answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail')
            
            result_dict = {
                'title' : answer['items'][i]['volumeInfo']['title'],
                'subtitle' : answer['items'][i]['volumeInfo'].get('subtitle'),
                'description' : answer['items'][i]['volumeInfo'].get('description'),
                'count' : answer['items'][i]['volumeInfo'].get('pageCount'),
                'categories' : answer['items'][i]['volumeInfo'].get('categories'),
                'rating' : answer['items'][i]['volumeInfo'].get('pageRating'),
                'thumbnail' : thumb,
                
                'preview' : answer['items'][i]['volumeInfo'].get('previewLink')

            }

            
            result_list.append(result_dict)
        context = {'form':form, 'results': result_list}
        return render(request,'dashboard/books.html',context)
        
    else :
        form = DashboardForm()
    context = {'form':form}
    return render(request,"dashboard/books.html",context)


#Dictionary

def dictionary(request):
    if request.method == "POST":
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/" + text
        r = requests.get(url)
        answer = r.json()
        try: 
            
            phonetics = answer[0]['phonetics'][0]['text']
            #print(phonetics)
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            #print(definition)
            try :
                example = answer[0]['meanings'][0]['definitions'][0]['example']
            except :
                example = ''
            #print(example)
            synonyms = answer[0]['meanings'][0]['definitions'][0]['synonyms']
            #print(synonyms)
            audio = answer[0]['phonetics'][0]['audio']
            #print(audio)
            
            context = { 
                'form':form,
                'input':text,
                'phonetics':phonetics,
                'audio':audio,
                'definition':definition,
                'example':example,
                'synonyms':synonyms
            }
        except:
            context = {
                'form':form,
                'input':''
            }
        return render(request,"dashboard/dictionary.html",context)
        
    else :
        form = DashboardForm()
        context = {'form':form}
        return render(request,"dashboard/dictionary.html",context)


def wiki(request):
    if request.method == "POST":
        text = request.POST['text']
        form = DashboardForm(request.POST)
        search = wikipedia.page(text)
        context = {
            'form':form,
            'title':search.title,
            'link':search.url,
            'details':search.summary,

        }
        return render(request,'dashboard/wiki.html',context)
    else:
        form = DashboardForm()
        context = {'form':form}
    return render(request,'dashboard/wiki.html',context)


def conversion(request):
    if request.method == "POST":
        form = ConversionForm(request.POST)
        if request.POST['measurement'] == 'length':
            measurement_form = CoversionLengthForm()
            context = {
            'form':form,
            'm_form': measurement_form,
            'input':True
            }
            if 'input' in request.POST :
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0 :
                    if first == 'yard' and second == 'foot':
                        answer = f'{input} yard = {int(input)*3} foot'
                    if first == 'foot' and second == 'yard':
                        answer = f'{input} foot = {int(input)/3} yard'

                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer

                }    
        
        if request.POST['measurement'] == 'mass':   
            measurement_form = CoversionMassForm()
            context = {
            'form':form,
            'm_form': measurement_form,
            'input':True
            }
            if 'input' in request.POST :
                first = request.POST['measure1']
                second = request.POST['measure2']
                input = request.POST['input']
                answer = ''
                if input and int(input) >=0 :
                    if first == 'pound' and second == 'kilogram':
                        answer = f'{input} pound = {int(input)*0.453592} kilogram'
                    if first == 'kilogram' and second == 'pound':
                        answer = f'{input} kilogram = {int(input)*2.20462} pound'

                context = {
                    'form':form,
                    'm_form':measurement_form,
                    'input':True,
                    'answer':answer
                    
                } 
    else:
        form = ConversionForm()
        context = {
            'form':form,
            'input':False
        }
    return render(request,'dashboard/conversion.html',context)


#Register
def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username}!')
            return redirect('login')
    else:         
        form = UserRegistrationForm()
    context = {
        'form':form
    }
    return render(request,'dashboard/register.html',context)

def profile(request):
    homeworks = Homework.objects.filter(is_finished= False, user = request.user)
    todos = Todo.objects.filter(is_finished = False, user = request.user)

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False
    
    if len(todos) == 0:
        todo_done = True
    else:
        todo_done = False

    context = {
        'homeworks':homeworks,
        'todos':todos,
        'homework_done':homework_done,
        'todo_done' : todo_done
    }
    
    return render(request,'dashboard/profile.html',context)

