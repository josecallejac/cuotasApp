from django.shortcuts import render, get_object_or_404
from django.db.models import Q, Min, Max, Count
from django.utils import timezone
from .models import Evento, Cuota, Deporte, CasaApuestas, TipoCuota


def index(view):
    """Vista principal - Dashboard con eventos próximos"""
    # Obtener eventos activos (no finalizados y futuros)
    eventos_proximos = Evento.objects.filter(
        finalizado=False,
        fecha_evento__gte=timezone.now()
    ).select_related('deporte').prefetch_related('cuotas')[:20]
    
    # Obtener deportes disponibles
    deportes = Deporte.objects.all()
    
    # Obtener estadísticas
    total_eventos = eventos_proximos.count()
    total_casas = CasaApuestas.objects.filter(activa=True).count()
    
    context = {
        'eventos': eventos_proximos,
        'deportes': deportes,
        'total_eventos': total_eventos,
        'total_casas': total_casas,
    }
    return render(view, 'comparador/index.html', context)


def evento_detalle(request, evento_id):
    """Vista detallada de un evento con comparación de cuotas"""
    evento = get_object_or_404(
        Evento.objects.select_related('deporte'),
        id=evento_id
    )
    
    # Obtener todas las cuotas agrupadas por tipo
    cuotas = Cuota.objects.filter(evento=evento).select_related(
        'casa_apuestas', 'tipo_cuota'
    ).order_by('tipo_cuota', 'opcion', '-valor')
    
    # Organizar cuotas por tipo
    cuotas_por_tipo = {}
    for cuota in cuotas:
        tipo_key = cuota.tipo_cuota.codigo
        if tipo_key not in cuotas_por_tipo:
            cuotas_por_tipo[tipo_key] = {
                'nombre': cuota.tipo_cuota.nombre,
                'opciones': {}
            }
        
        opcion = cuota.opcion
        if opcion not in cuotas_por_tipo[tipo_key]['opciones']:
            cuotas_por_tipo[tipo_key]['opciones'][opcion] = []
        
        cuotas_por_tipo[tipo_key]['opciones'][opcion].append(cuota)
    
    # Encontrar mejores cuotas por opción
    mejores_cuotas = {}
    for cuota in cuotas:
        key = f"{cuota.tipo_cuota.codigo}_{cuota.opcion}"
        if key not in mejores_cuotas or cuota.valor > mejores_cuotas[key].valor:
            mejores_cuotas[key] = cuota
    
    context = {
        'evento': evento,
        'cuotas_por_tipo': cuotas_por_tipo,
        'mejores_cuotas': mejores_cuotas,
    }
    return render(request, 'comparador/evento_detalle.html', context)


def eventos_por_deporte(request, deporte_slug):
    """Vista de eventos filtrados por deporte"""
    deporte = get_object_or_404(Deporte, slug=deporte_slug)
    
    eventos = Evento.objects.filter(
        deporte=deporte,
        finalizado=False,
        fecha_evento__gte=timezone.now()
    ).select_related('deporte').prefetch_related('cuotas')
    
    # Filtros adicionales
    liga = request.GET.get('liga')
    if liga:
        eventos = eventos.filter(liga__icontains=liga)
    
    pais = request.GET.get('pais')
    if pais:
        eventos = eventos.filter(pais__icontains=pais)
    
    # Obtener ligas y países únicos para filtros
    ligas = Evento.objects.filter(
        deporte=deporte,
        finalizado=False
    ).values_list('liga', flat=True).distinct()
    
    paises = Evento.objects.filter(
        deporte=deporte,
        finalizado=False
    ).values_list('pais', flat=True).distinct()
    
    context = {
        'deporte': deporte,
        'eventos': eventos,
        'ligas': [l for l in ligas if l],
        'paises': [p for p in paises if p],
        'liga_seleccionada': liga,
        'pais_seleccionado': pais,
    }
    return render(request, 'comparador/eventos_por_deporte.html', context)


def mejores_cuotas(request):
    """Vista con las mejores cuotas disponibles"""
    # Obtener el tipo de cuota seleccionado (por defecto 1X2)
    tipo_codigo = request.GET.get('tipo', '1x2')
    
    try:
        tipo_cuota = TipoCuota.objects.get(codigo=tipo_codigo)
    except TipoCuota.DoesNotExist:
        tipo_cuota = TipoCuota.objects.first()
    
    # Obtener eventos con sus mejores cuotas
    eventos = Evento.objects.filter(
        finalizado=False,
        fecha_evento__gte=timezone.now()
    ).select_related('deporte')
    
    # Para cada evento, encontrar la mejor cuota
    eventos_con_mejores_cuotas = []
    for evento in eventos:
        cuotas = Cuota.objects.filter(
            evento=evento,
            tipo_cuota=tipo_cuota
        ).select_related('casa_apuestas').order_by('opcion', '-valor')
        
        if cuotas.exists():
            # Agrupar por opción
            opciones = {}
            for cuota in cuotas:
                if cuota.opcion not in opciones:
                    opciones[cuota.opcion] = cuota
            
            eventos_con_mejores_cuotas.append({
                'evento': evento,
                'cuotas': opciones
            })
    
    # Obtener todos los tipos de cuota disponibles
    tipos_cuota = TipoCuota.objects.all()
    
    context = {
        'eventos_cuotas': eventos_con_mejores_cuotas,
        'tipo_cuota_actual': tipo_cuota,
        'tipos_cuota': tipos_cuota,
    }
    return render(request, 'comparador/mejores_cuotas.html', context)


def buscar(request):
    """Vista de búsqueda de eventos"""
    query = request.GET.get('q', '')
    resultados = []
    
    if query:
        resultados = Evento.objects.filter(
            Q(equipo_local__icontains=query) |
            Q(equipo_visitante__icontains=query) |
            Q(liga__icontains=query),
            finalizado=False,
            fecha_evento__gte=timezone.now()
        ).select_related('deporte')[:50]
    
    context = {
        'query': query,
        'resultados': resultados,
    }
    return render(request, 'comparador/buscar.html', context)


def casas_apuestas(request):
    """Vista de todas las casas de apuestas"""
    casas = CasaApuestas.objects.filter(activa=True).annotate(
        total_cuotas=Count('cuotas')
    )
    
    context = {
        'casas': casas,
    }
    return render(request, 'comparador/casas_apuestas.html', context)
