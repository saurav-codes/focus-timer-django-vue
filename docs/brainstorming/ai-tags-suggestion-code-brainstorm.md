# AI Task Enrichment: Pseudocode Sketch

This document outlines high-level pseudo-code for integrating the AI enrichment feature into our Django + Vue.js 3 stack, covering both backend and frontend.

---

## 1. Backend (Django / DRF / Celery)

### 1.1 models.py
```python
# apps/core/models.py
class Task(models.Model):
    # existing fields...
    parent_task = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.CASCADE, related_name='subtasks'
    )
    # other fields unchanged
```

### 1.2 serializers.py
```python
# apps/core/serializers.py
class TaskSerializer(serializers.ModelSerializer):
    # include parent_task, subtasks, tags, project, duration
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'parent_task', 'subtasks',
                  'tags', 'project', 'duration', 'duration_display', 'ai_error']
```

### 1.3 views.py (POST /api/tasks/)
```python
class TasksApiView(APIView):
    def post(self, request):
        # parse ai_assist flag
        ai_flag = request.data.get('ai_assist', False)
        # create Task instance normally
        task = Task.objects.create(user=request.user, **validated_data)
        if ai_flag and request.user.ai_assist_enabled:
            if rate_limit_check(request.user):
                enqueue_ai_enrichment(task.id, user_id)
            else:
                # annotate response
                serializer = TaskSerializer(task)
                return Response({**serializer.data, 'ai_error': 'rate_limit'}, status=201)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=201)
```

### 1.4 Celery task
```python
# apps/core/tasks.py
@app.task
def enrich_task(task_id, user_id):
    if not rate_limit_check(user_id):
        Task.objects.filter(id=task_id).update(ai_error='rate_limit')
        return
    # prepare prompt with existing title, description, user projects/tags
    prompt = build_prompt(task_id, user_id)
    result = call_openai(prompt)
    data = parse_json(result)
    # update Task: set parent_task for subtasks, create child tasks, assign tags/project/duration
    with transaction.atomic():
        parent = Task.objects.get(id=task_id)
        for text in data['subtasks']:
            Task.objects.create(
                user=parent.user,
                title=text,
                parent_task=parent,
                status=parent.status,
            )
        parent.tags.set(data['tags'])
        parent.project = Project.objects.filter(user=parent.user, title=data['project']).first()
        parent.duration = parse_duration(data['duration'])
        parent.save()
```

### 1.5 Rate Limiter Logic (Redis)
```python
def rate_limit_check(user_id):
    # for each bucket in ['min', 'hour', 'day']:
    #   refill tokens based on elapsed time
    #   if tokens > 0: decrement & continue
    #   else: return False
    return True
```

---

## 2. Frontend (Vue 3 + Pinia)

### 2.1 Pinia store action
```js
// taskstore.js
async function createTask(payload) {
  const response = await api.createTask(payload)
  // if response.ai_error == 'rate_limit':
  //   disable toggle UI, show snackbar
  if (response.data.ai_error === 'rate_limit') {
    uiStore.disableAiToggle()
    snackbar.add("AI limit reached", "OK")
  }
  // optimistic UI: add to store then poll enrichment
  if (payload.ai_assist) {
    pollEnrichment(response.data.id)
  }
  return response.data
}

function pollEnrichment(taskId) {
  let attempts = 0
  const intervalId = setInterval(async () => {
    attempts += 1
    const updated = await api.getTask(taskId)
    if (updated.subtasks.length || updated.ai_error) {
      store.updateTask(updated)
      clearInterval(intervalId)
    } else if (attempts >= 8) {
      clearInterval(intervalId)
    }
  }, 2000)
}
```

### 2.2 Task creation component
```vue
<!-- TaskCreationPopup.vue -->
<template>
  <input v-model="title" placeholder="Task title" />
  <ToggleSwitch v-model="aiAssist" label="AI-Assist" />
  <button @click="saveTask">Save</button>
</template>

<script>
function saveTask() {
  taskStore.createTask({
    title, ai_assist: aiAssist
  })
}
</script>
```

### 2.3 UI Toggle state
- Persist `aiAssistEnabled` in both Pinia and localStorage.
- Read initial setting from backend user profile.

---

## 3. Flow Summary

1. **User** toggles AI-Assist and creates a task.
2. **Backend** saves task, enqueues enrichment job (if under rate limit).
3. **Celery** worker calls GPT, parses JSON, writes subtasks & metadata.
4. **Frontend** polls `/api/tasks/{id}` until subtasks appear.
5. **UI** updates automatically, showing enriched fields.
