from rest_framework.pagination import PageNumberPagination


class Paginacao(PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 1000
    page_size = 10

    def get_page_size(self, request):
        if self.page_size_query_param:
            page_size = min(
                int(
                    request.query_params.get(self.page_size_query_param, self.page_size)
                ),
                self.max_page_size,
            )
            if page_size > 0:
                return page_size
            else:
                return None

        return self.page_size

    def paginate_queryset(self, queryset, request, view=None):
        """
        Pagina um queryset, se necessário, retornando um
        objeto de página ou `none` se a paginação não estiver
        configurada para esta visualização.
        """
        page_size = self.get_page_size(request)
        if not page_size:
            return None

        paginator = self.django_paginator_class(queryset, page_size)
        page_number = request.query_params.get(self.page_query_param, 1)
        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            self.page = paginator.page(page_number)
        except Exception:
            self.page = paginator.page(1)

        if paginator.num_pages > 1 and self.template is not None:
            self.display_page_controls = True

        self.request = request
        return list(self.page)


def paginacao(page):
    max_page = 15
    min_page = 5
    page_size = 10
    if page and int(page) > max_page:
        page_size = max_page
    elif page and int(page) < min_page:
        page_size = min_page
    elif page:
        page_size = int(page)

    return page_size


def chunks(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i : i + n]


def paginacao_list(lista, page_size):
    return list(chunks(lista, page_size))


def ordena_lista(lista_pessoa, ordenacao):
    reverse = False

    order = ordenacao if ordenacao else "nome"
    if "-" in order:
        order = order.replace("-", "")
        reverse = True

    if order == "data_nascimento":
        lista_data_vazia = [
            item for item in lista_pessoa if not item["data_nascimento"]
        ]
        lista_com_data = [item for item in lista_pessoa if item["data_nascimento"]]
        lista = sorter_list(order, lista_com_data, reverse)
        lista.extend(lista_data_vazia)
    else:
        lista = sorter_list(order, lista_pessoa, reverse)

    return lista


def sorter_list(order, lista, reverse):
    return sorted(lista, key=lambda row: row[order], reverse=reverse)
