<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\DependencyInjection\Attribute\Autowire;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Annotation\Route;

final class ContactController extends AbstractController
{
    public function __construct(
        #[Autowire(param: 'app.contact.email')] private readonly string $contactEmail,
        #[Autowire(param: 'app.contact.phone')] private readonly string $contactPhone,
        #[Autowire(param: 'app.contact.address')] private readonly string $contactAddress,
    ) {}

    #[Route('/contact', name: 'app_contact')]
    public function index(): Response
    {
        return $this->render('contact/index.html.twig', [
            'contact_data' => [
                'email' => $this->contactEmail,
                'phone' => $this->contactPhone,
                'address' => $this->contactAddress,
            ],
        ]);
    }
}
