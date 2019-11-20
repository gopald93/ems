from django.shortcuts import render
from django.contrib.auth.models import User
from poll.models import *
from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from poll.forms import PollForm, ChoiceForm
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import CreateView
from django.db.models import Q
from django.shortcuts import render, reverse, redirect, get_object_or_404

@login_required(login_url="/login/")
def index(request):
    context={}
    questions= Question.objects.all()
    context['title']='polls'
    context['questions']=questions
    return render(request,'poll/index.html',context)

@login_required(login_url="/login/")
def details(request,id=None):
    context={}
    try:
        question= Question.objects.get(id=id)
    except:
        raise Http404   
    context['question']=question
    return render(request,'poll/details.html',context)

    
@login_required(login_url="/login/")
def poll(request,id=None):
    if request.method == "GET":
        try:
            question=Question.objects.get(id=id)
        except:
            raise Http404   
        context={}
        context['question']=question
        return render(request,'poll/poll.html',context)
    if request.method=="POST":
        try:
            messages=None
            user_id=1
            data = request.POST 
            answer_obj= Answer.objects.create(user_id=user_id,choice_id= data["choice"])
            if answer_obj: 
                messages="you are successfully choose the question"
            else:
                messages="problem in choosing  the answer"
        except Exception as e:
            print(e)    
        return HttpResponse(messages)


class PollView(View):
    decorators = [login_required]
    @method_decorator(decorators)
    def get(self, request, id=None):
        if id:
            question = get_object_or_404(Question, id=id)
            poll_form = PollForm(instance=question)
            choices = question.choice_set.all()
            if choices:
                choice_forms = [ChoiceForm(prefix=str(
                    choice.id), instance=choice) for choice in choices]
            else:
                choice_forms = [ChoiceForm(request.POST, prefix=str(
                    x), instance=Choice()) for x in range(0, 3)]
                
            template = 'poll/edit_poll.html'
        else:
            poll_form = PollForm(instance=Question())
            choice_forms = [ChoiceForm(prefix=str(
                x), instance=Choice()) for x in range(3)]
            template = 'poll/new_poll.html'
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, template, context)

    @method_decorator(decorators)
    def post(self, request, id=None):
        context = {}
        if id:
            return self.put(request, id)
        poll_form = PollForm(request.POST, instance=Question())
        choice_forms = [ChoiceForm(request.POST, prefix=str(
            x), instance=Choice()) for x in range(0, 3)]
        if poll_form.is_valid() and all([cf.is_valid() for cf in choice_forms]):
            new_poll = poll_form.save(commit=False)
            new_poll.created_by = request.user
            new_poll.save()
            for cf in choice_forms:
                new_choice = cf.save(commit=False)
                new_choice.question = new_poll
                new_choice.save()
            return HttpResponseRedirect(reverse('polls_list'))   
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, 'poll/new_poll.html', context)

    @method_decorator(decorators)
    def put(self, request, id=None):
        print("put---->")
        context = {}
        question = get_object_or_404(Question, id=id)
        poll_form = PollForm(request.POST, instance=question)
        choice_forms = [ChoiceForm(request.POST, prefix=str(
            choice.id), instance=choice) for choice in question.choice_set.all()]
        if poll_form.is_valid() and all([cf.is_valid() for cf in choice_forms]):
            new_poll = poll_form.save(commit=False)
            new_poll.created_by = request.user
            new_poll.save()
            for cf in choice_forms:
                new_choice = cf.save(commit=False)
                new_choice.question = new_poll
                new_choice.save()
            return redirect('polls_list')
        context = {'poll_form': poll_form, 'choice_forms': choice_forms}
        return render(request, 'poll/edit_poll.html', context)

    # @method_decorator(decorators)
    # def delete(self, request, id=None):
    #     question = get_object_or_404(Question)
    #     question.delete()
    #     return redirect('polls_list')


@login_required(login_url="/login/")
def poll_delete(request,id=None):
    context={}
    question = get_object_or_404(Question,id=id)
    if request.method=="POST":
        question.delete()
        return HttpResponseRedirect(reverse('polls_list'))   
    else:
        context['user']=question
        return render(request,'employee/delete.html',context)


@login_required(login_url="/login/")
def vote_poll(request, id=None):
    context = {}
    try:
        question = Question.objects.get(id=id)
    except:
        raise Http404
    context["question"] = question

    if request.method == "POST":
        user_id = 1
        print(request.POST)
        data = request.POST
        ret = Answer.objects.create(user_id=user_id, choice_id=data['choice'])
        if ret:
            return HttpResponseRedirect(reverse('poll_details', args=[question.id]))
        else:
            context["error"] = "Your vote is not done successfully"
            return render(request, 'poll/poll.html', context)
    else:
        return render(request, 'poll/poll.html', context)