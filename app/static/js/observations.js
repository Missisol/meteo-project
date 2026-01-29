// Popover for flash messages
const popoverFlash = document.getElementById('popover-flash') // popover для flash сообщений
const alert = document.querySelector('.alert')
// create dialog
const createDialog = document.querySelector('#create-dialog') // диалог создания
const createButton = document.querySelector('#create-button') // кнопка открытия диалога
const closeCreateDialog = document.querySelector('#create-close') // кнопка закрытия диалога
// delete dialog
const deleteButtons = document.querySelectorAll('#delete-button') // кнопки открытия диалога удаления
const deleteDialog = document.querySelector('#delete-dialog') // диалог удаления
const closeDeleteDialog = document.querySelector('#delete-close') // кнопка закрытия диалога
// edit dialog
const editButtons = document.querySelectorAll('#edit-button') // кнопки открытия диалога редактирования
const editDialog = document.querySelector('#edit-dialog') // диалог редактирования
const closeEditDialog = document.querySelector('#edit-close') // кнопка закрытия диалога редактирования
// filter dialog
const filterButton = document.querySelector('#filter-button')
const filterDialog = document.querySelector('#filter-dialog')
const closeFilterDialog = document.querySelector('#filter-close')
const filterForm = document.querySelector('#filter-form')
const filterStartDate = document.querySelector('#start_date')
const filterEndDate = document.querySelector('#end_date')
const filterFormError = document.querySelector('#filter-form-error')
const buttonSwapDates = document.querySelector('#button-swap-dates')

if (alert) {
  if (alert.textContent) {
    popoverFlash.showPopover()

    setTimeout(() => {
      popoverFlash.hidePopover()
      alert.textContent = ''
    }, 2000)
  }
}

async function getObservationData(id) {
  editDialog.querySelector('#editId').value = id
  try {
    const response = await fetch(`/api/observations/${id}/data`)
    const data = await response.json()
    editDialog.querySelector('#created-at').textContent = data.created_at
    editDialog.querySelector('#cloudiness').value = data.cloudiness || 'clear'
    editDialog.querySelector('#precipitation').value = data.precipitation || 'none'
    editDialog.querySelector('#precipitation-rate').value = data.precipitation_rate || 'none'
    editDialog.querySelector('#snow-depth').value = data.snow_depth || 0
  } catch (error) {
    console.error('Error fetching observation data:', error)
    alert('Ошибка при загрузке данных записи')
  }
}

function validateFilterDates() {
  if (filterStartDate && filterEndDate && filterStartDate.value && filterEndDate.value) {
    if (filterStartDate.value > filterEndDate.value) {
      return {
        error: 'Дата начала периода больше даты конца периода'
      }
    }
  }
  return { valid: true }
}

function initFilterForm() {
  if (filterForm) {
    filterForm.addEventListener('submit', (e) => {
      const validation = validateFilterDates()
      if (validation.error) {
        e.preventDefault()
        if (filterFormError) {
          filterFormError.textContent = validation.error
        }
        return false
      } else {
        if (filterFormError) {
          filterFormError.textContent = ''
        }
      }
    })
  }

  if (buttonSwapDates && filterStartDate && filterEndDate) {
    buttonSwapDates.addEventListener('click', () => {
      if (filterStartDate.value && filterEndDate.value) {
        const temp = filterStartDate.value
        filterStartDate.value = filterEndDate.value
        filterEndDate.value = temp
        if (filterFormError) {
          filterFormError.textContent = ''
        }
      }
    })
  }
}

function init() {
  if (createDialog && createButton) {
    createButton.addEventListener('click', () => {
      createDialog.showModal()
    })
  }

    if (createDialog &&closeCreateDialog) {
    closeCreateDialog.addEventListener('click', () => {
      createDialog.close()
    })
  }

  if (editButtons.length && editDialog) {
    editButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        getObservationData(id)
        editDialog.showModal()
      })
    })
  }

  if (closeEditDialog && editDialog) {
    closeEditDialog.addEventListener('click', () => {
      editDialog.hidePopover()
    })
  }


  if (closeFilterDialog && filterDialog) {
    closeFilterDialog.addEventListener('click', () => {
      filterDialog.close()
    })
  }

  if (closeDeleteDialog && deleteDialog) {
    closeDeleteDialog.addEventListener('click', () => {
      deleteDialog.close()
    })
  }

  if (deleteButtons.length && deleteDialog) {
    deleteButtons.forEach((button) => {
      button.addEventListener('click', (e) => {
        const id = e.currentTarget.dataset.id
        if (!id) return
        const form = deleteDialog.querySelector(`#delete-form`)
        if (form) {
          form.action = `/api/observations/${id}/delete`
        }
         deleteDialog.showModal()
      })
    })
  }

  if (filterButton && filterDialog) {
    filterButton.addEventListener('click', () => {
      filterDialog.showModal()
    })
  }

  initFilterForm()
}

init()