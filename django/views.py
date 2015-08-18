@login_required
@transaction.commit_on_success
def create_waybill(request, id):
    if Register.objects.filter(id=id).exists() and Register.objects.get(id=id).sender == request.sender:
        return create_response([id], user_friendly=True)
    else:
        return HttpResponseRedirect("/")
