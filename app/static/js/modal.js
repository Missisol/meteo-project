// Popover for flash messages
const popoverFlash = document.querySelector('#popover-flash') // popover для flash сообщений
const alert = document.querySelector('.alert')
// Filter dialog elements
const filterButton = document.querySelector('#filter-button')
const filterDialog = document.querySelector('#filter-dialog')
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
  if (filterButton && filterDialog) {
    filterButton.addEventListener('click', () => {
      filterDialog.showModal()
    })
  }

  initFilterForm()
}

init()
