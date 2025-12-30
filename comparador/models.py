from django.db import models
from django.utils import timezone

class CasaApuestas(models.Model):
    """Modelo para representar una casa de apuestassss"""
    nombre = models.CharField(max_length=100, unique=True)
    logo = models.URLField(blank=True, null=True, help_text="URL del logo")
    url = models.URLField(help_text="Sitio web de la casa de apuestas")
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Casa de Apuestas"
        verbose_name_plural = "Casas de Apuestas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Deporte(models.Model):
    """Modelo para representar diferentes deportes"""
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    icono = models.CharField(max_length=50, blank=True, help_text="Clase de ícono (ej: fa-futbol)")
    
    class Meta:
        verbose_name = "Deporte"
        verbose_name_plural = "Deportes"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Evento(models.Model):
    """Modelo para representar un evento deportivo"""
    deporte = models.ForeignKey(Deporte, on_delete=models.CASCADE, related_name='eventos')
    equipo_local = models.CharField(max_length=150)
    equipo_visitante = models.CharField(max_length=150)
    fecha_evento = models.DateTimeField()
    liga = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, blank=True)
    finalizado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['fecha_evento']
        indexes = [
            models.Index(fields=['fecha_evento', 'finalizado']),
        ]
    
    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante}"
    
    def esta_activo(self):
        """Verifica si el evento aún está activo para apuestas"""
        return not self.finalizado and self.fecha_evento > timezone.now()


class TipoCuota(models.Model):
    """Tipos de apuestas disponibles"""
    nombre = models.CharField(max_length=50, unique=True, help_text="Ej: 1X2, Over/Under, Handicap")
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Tipo de Cuota"
        verbose_name_plural = "Tipos de Cuotas"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Cuota(models.Model):
    """Modelo para representar las cuotas de apuestas"""
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='cuotas')
    casa_apuestas = models.ForeignKey(CasaApuestas, on_delete=models.CASCADE, related_name='cuotas')
    tipo_cuota = models.ForeignKey(TipoCuota, on_delete=models.CASCADE, related_name='cuotas')
    
    # Opciones para el tipo de apuesta (1, X, 2, Over, Under, etc.)
    opcion = models.CharField(max_length=50, help_text="Ej: 1, X, 2, Over 2.5, Under 2.5, etc.")
    
    # Valor de la cuota
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Control de cambios
    valor_anterior = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Cuota"
        verbose_name_plural = "Cuotas"
        ordering = ['-valor']
        unique_together = [['evento', 'casa_apuestas', 'tipo_cuota', 'opcion']]
        indexes = [
            models.Index(fields=['evento', 'tipo_cuota', 'opcion']),
        ]
    
    def __str__(self):
        return f"{self.evento} - {self.tipo_cuota} {self.opcion}: {self.valor} ({self.casa_apuestas})"
    
    def cambio_cuota(self):
        """Retorna el cambio en la cuota si hubo actualización"""
        if self.valor_anterior:
            return self.valor - self.valor_anterior
        return 0
    
    def tendencia(self):
        """Retorna 'subida', 'bajada' o 'sin_cambio'"""
        cambio = self.cambio_cuota()
        if cambio > 0:
            return 'subida'
        elif cambio < 0:
            return 'bajada'
        return 'sin_cambio'
